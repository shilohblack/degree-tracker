"""Degree tracker.

Answers two different questions about the same course list:

  "Where am I now?"     -> the completed_* functions, from posted grades only
  "Where does the plan  -> the planned_* functions, which include courses
   land?"                  not taken yet

Both matter. The first is your transcript. The second is whether you graduate.

Run it:    python tracker.py
Check it:  python check.py
"""

from data import COURSES, REQUIREMENTS, MAJOR_CATEGORIES

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


def is_major(course):
    """True if the course counts toward the 50-unit major requirement.

    MAJOR_CATEGORIES lives in data.py and is the single source of truth.
    Do not write a second copy of this list anywhere.
    """
    return course["category"] in MAJOR_CATEGORIES


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

    A course counts only if its category is "Major Elective". EPID 309 is
    deliberately categorised "Other Upper Division" because it is not on the
    audit's approved list, so it is excluded here automatically. There is no
    second approved-codes list to keep in sync.
    """
    return _units(courses, lambda c: is_planned(c) and c["category"] == "Major Elective")


def planned_gen_ed_units(courses):
    """Units categorised as general education.

    This UNDER-COUNTS on purpose. Each course here carries one category, but
    UA lets a single course satisfy both a major requirement and a GE one.
    MCB 181R, for example, is Foundation Biology here and also satisfies the
    Natural Scientist GE. The real audit figure is higher than this.
    """
    return _units(courses, lambda c: is_planned(c) and c["category"] == "Gen Ed")


# --------------------------------------------------------------- the report

ROWS = [
    ("total units", "total_units", earned_units, planned_total_units),
    ("upper division units", "upper_division",
     completed_upper_division_units, planned_upper_division_units),
    ("major units", "major_units",
     completed_major_units, planned_major_units),
    ("major upper division", "major_upper_division",
     completed_major_upper_division_units, planned_major_upper_division_units),
    ("major elective units", "major_electives",
     lambda cs: _units(cs, lambda c: is_completed(c) and c["category"] == "Major Elective"),
     planned_elective_units),
    ("general education units", "gen_ed",
     lambda cs: _units(cs, lambda c: is_completed(c) and c["category"] == "Gen Ed"),
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
    print("-" * 60)
    print("General education under-counts: a course has one category here,")
    print("but UA lets one course satisfy both a major and a GE requirement.")


if __name__ == "__main__":
    courses, source = load_courses()
    result = calculate_gpa(courses)
    print(f"source                      : {source}")
    print(f"Courses with a posted grade : {count_courses(courses)}")
    print(f"Cumulative GPA              : {result['gpa']}"
          f"  ({result['total_points']:.0f} points / {result['gpa_units']:.0f} units)")
    print()
    requirement_report(courses)
