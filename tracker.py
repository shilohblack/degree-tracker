"""Degree tracker.

Answers two different questions about the same course list:

  "Where am I now?"     -> the completed_* functions, from posted grades only
  "Where does the plan  -> the planned_* functions, which include courses
   land?"                  not taken yet

Both matter. The first is your transcript. The second is whether you graduate.

Run it:    python tracker.py
Check it:  python check.py
"""

import allocate
from data import COURSES, COURSE_REQUIREMENTS, REQUIREMENTS, MAJOR_POOLS

GRADE_POINTS = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "E": 0.0}


def load_courses():
    """The course list to report on.

    If my_data.py exists it wins, so you can run this against your own
    record without touching the published sample. my_data.py is gitignored.
    Every function below takes `courses` as an argument, so the tests can
    still pin themselves to the sample regardless of what this returns.
    """
    try:
        from my_data import COURSES as mine
        return mine, "my_data.py"
    except ImportError:
        return COURSES, "data.py (sample)"


# ----------------------------------------------------------------- predicates

def is_excluded(course):
    """True if UA removed this attempt from the record entirely.

    Only your first MATH 122B attempt. It counts nowhere: not units,
    not grade points, not even as attempted.
    """
    return course["excluded"]


def is_completed(course):
    """True if the course has a posted grade, including S."""
    return not is_excluded(course) and course["grade"] is not None


def is_planned(course):
    """True if the course is part of the plan, taken or not.

    This is the whole plan minus the excluded repeat.
    """
    return not is_excluded(course)


def grade_points(grade):
    """Points per unit for a letter grade.

    Returns None for S and for ungraded courses, which is what keeps them
    out of the GPA. An E is 0.0, not None: it still counts against you.
    """
    return GRADE_POINTS.get(grade)


def is_gen_ed(course):
    """True if the course carries a general education designation.

    This is an attribute, not a category. A course can be Foundation Biology
    AND general education at the same time, which is how real degree audits
    work: BIOL 101 counts toward the major and satisfies the natural science
    requirement from the same four units.
    """
    return course["gen_ed"]


def pool_of(course):
    """The named requirement this course fills, or None.

    After the allocator has run, a course carries a single resolved "pool".
    Before it has, fall back to the first option it is eligible for, so the
    functions below work on raw data too.
    """
    if "pool" in course:
        return course["pool"]
    return course["pools"][0] if course["pools"] else None


def is_major(course):
    """True if the course counts toward the 50-unit major requirement.

    MAJOR_POOLS lives in data.py and is the single source of truth.
    Do not write a second copy of this list anywhere.
    """
    return pool_of(course) in MAJOR_POOLS


def _units(courses, keep):
    """Add up the units of every course for which keep(course) is True."""
    total = 0.0
    for course in courses:
        if keep(course):
            total += course["units"]
    return total


# ------------------------------------------------------- where you are now

def count_courses(courses):
    """How many courses have a posted grade."""
    return sum(1 for c in courses if is_completed(c))


def earned_units(courses):
    """Units actually earned. Includes S grades, which earn credit."""
    return _units(courses, is_completed)


def completed_upper_division_units(courses):
    return _units(courses, lambda c: is_completed(c) and c["upper_division"])


def completed_major_units(courses):
    return _units(courses, lambda c: is_completed(c) and is_major(c))


def completed_major_upper_division_units(courses):
    return _units(
        courses,
        lambda c: is_completed(c) and c["upper_division"] and is_major(c),
    )


def calculate_gpa(courses):
    """Cumulative GPA, by UA's rules.

    Three things stay out of the fraction: excluded repeats, S grades
    (units but no points), and courses not graded yet.
    """
    total_points = 0.0
    gpa_units = 0.0

    for course in courses:
        if not is_completed(course):
            continue
        points = grade_points(course["grade"])
        if points is None:          # an S grade
            continue
        total_points += points * course["units"]
        gpa_units += course["units"]

    gpa = round(total_points / gpa_units, 3) if gpa_units else 0.0
    return {
        "gpa": gpa,
        "total_points": total_points,
        "gpa_units": gpa_units,
        "earned_units": earned_units(courses),
    }


# ------------------------------------------------------ where the plan lands

def planned_total_units(courses):
    return _units(courses, is_planned)


def planned_upper_division_units(courses):
    return _units(courses, lambda c: is_planned(c) and c["upper_division"])


def planned_major_units(courses):
    return _units(courses, lambda c: is_planned(c) and is_major(c))


def planned_major_upper_division_units(courses):
    return _units(
        courses,
        lambda c: is_planned(c) and c["upper_division"] and is_major(c),
    )


def planned_elective_units(courses):
    """Units from courses the audit accepts as major electives.

    A course counts only if the allocator assigned it to "Major Elective".
    EPID 309 has no pools at all, because it is not on the audit's approved
    list, so it is excluded automatically. There is no second approved-codes
    list to keep in sync.
    """
    return _units(courses, lambda c: is_planned(c) and pool_of(c) == "Major Elective")


def planned_gen_ed_units(courses):
    """Units carrying a general education designation."""
    return _units(courses, lambda c: is_planned(c) and is_gen_ed(c))


# --------------------------------------------------------------- the report

def measure(courses, key):
    """How many units a requirement has, by its key in REQUIREMENTS.

    allocate.best() uses this to score competing assignments, which is why
    it is a plain lookup rather than six separate calls.
    """
    return {
        "total_units": planned_total_units,
        "upper_division": planned_upper_division_units,
        "major_units": planned_major_units,
        "major_upper_division": planned_major_upper_division_units,
        "major_electives": planned_elective_units,
        "gen_ed": planned_gen_ed_units,
    }[key](courses)


def courses_in_pool(courses, pool):
    """How many planned courses are assigned to a named pool."""
    return sum(1 for c in courses if is_planned(c) and pool_of(c) == pool)


def score(resolved):
    """Rank an assignment: requirements met first, then smallest shortfall.

    Surplus deliberately counts for nothing. Banking three spare elective
    units is worth less than filling a requirement you cannot graduate
    without, and scoring surplus as credit makes the allocator prefer the
    former.

    Both kinds of requirement are counted. Unit requirements come from
    REQUIREMENTS, course-count requirements from COURSE_REQUIREMENTS. Leaving
    the second kind out is how an allocator ends up moving the only course
    that can satisfy a requirement somewhere else.
    """
    met = 0
    shortfall = 0.0
    for key, needed in REQUIREMENTS.items():
        have = measure(resolved, key)
        shortfall += min(have - needed, 0)   # surplus is waste, not credit
        met += have >= needed
    for pool, needed in COURSE_REQUIREMENTS.items():
        have = courses_in_pool(resolved, pool)
        shortfall += min(have - needed, 0)
        met += have >= needed
    return met, shortfall


def prepare(courses):
    """Resolve every contested course to one pool, best assignment first."""
    resolved, choices, _value = allocate.best(courses, score)
    return resolved, choices


ROWS = [
    ("total units", "total_units", earned_units, planned_total_units),
    ("upper division units", "upper_division",
     completed_upper_division_units, planned_upper_division_units),
    ("major units", "major_units",
     completed_major_units, planned_major_units),
    ("major upper division", "major_upper_division",
     completed_major_upper_division_units, planned_major_upper_division_units),
    ("major elective units", "major_electives",
     lambda cs: _units(cs, lambda c: is_completed(c) and pool_of(c) == "Major Elective"),
     planned_elective_units),
    ("general education units", "gen_ed",
     lambda cs: _units(cs, lambda c: is_completed(c) and is_gen_ed(c)),
     planned_gen_ed_units),
]


def requirement_report(courses):
    """Print every requirement with what you have and where the plan lands."""
    print(f"{'requirement':26}{'earned':>8}{'planned':>9}{'needed':>8}   status")
    print("-" * 60)
    for label, key, earned_fn, planned_fn in ROWS:
        needed = REQUIREMENTS[key]
        earned = earned_fn(courses)
        planned = planned_fn(courses)
        status = "PASS" if planned >= needed else "SHORT"
        print(f"{label:26}{earned:8.0f}{planned:9.0f}{needed:8}   {status}")
    for pool, needed in COURSE_REQUIREMENTS.items():
        have = courses_in_pool(courses, pool)
        done = sum(1 for c in courses if is_completed(c) and pool_of(c) == pool)
        status = "PASS" if have >= needed else "UNFILLED"
        print(f"{pool.lower() + ' (courses)':26}{done:8}{have:9}{needed:8}   {status}")
    print("-" * 60)


if __name__ == "__main__":
    raw, source = load_courses()
    courses, choices = prepare(raw)
    result = calculate_gpa(courses)

    print(f"source                      : {source}")
    print(f"Courses with a posted grade : {count_courses(courses)}")
    print(f"Cumulative GPA              : {result['gpa']}"
          f"  ({result['total_points']:.0f} points / {result['gpa_units']:.0f} units)")
    print()

    decisions = allocate.explain(raw, choices)
    if decisions:
        print("Allocator decisions")
        for line in decisions:
            print(f"  {line}")
        print()

    requirement_report(courses)
