"""GPA projection.

Where tracker.py says where you are, this says where you can get to.

Run it:  python projection.py
"""

from itertools import product

from tracker import (
    calculate_gpa,
    grade_points,
    is_completed,
    is_planned,
    load_courses,
)

LETTERS = ["A", "B", "C", "D", "E"]


def remaining_courses(courses):
    """Courses in the plan that do not have a grade yet.

    These are the ones you can still change. Everything else is history.
    """
    return [c for c in courses if is_planned(c) and not is_completed(c)]


def remaining_gpa_units(courses):
    """Units still to be graded. The denominator you have left to fill."""
    return float(sum(c["units"] for c in remaining_courses(courses)))


def final_gpa_units(courses):
    """GPA units you will have at graduation, if nothing changes."""
    return calculate_gpa(courses)["gpa_units"] + remaining_gpa_units(courses)


def average_needed(courses, target):
    """The average grade needed across every remaining unit to finish at target.

    Returns None if the target is impossible, which happens when even
    straight A grades would not get you there.
    """
    now = calculate_gpa(courses)
    remaining = remaining_gpa_units(courses)
    if remaining == 0:
        return None
    points_wanted = target * (now["gpa_units"] + remaining)
    needed = (points_wanted - now["total_points"]) / remaining
    return None if needed > 4.0 else round(needed, 3)


def ceiling(courses):
    """The best cumulative GPA still reachable, with straight A grades."""
    now = calculate_gpa(courses)
    remaining = remaining_gpa_units(courses)
    total = now["total_points"] + 4.0 * remaining
    return round(total / (now["gpa_units"] + remaining), 3)


def gpa_if(courses, assumed):
    """Cumulative GPA if the named courses earned the named grades.

    `assumed` maps a course code to a letter, e.g. {"ORGC 241": "B"}.
    Courses not named stay ungraded and stay out of the calculation.
    """
    now = calculate_gpa(courses)
    points = now["total_points"]
    units = now["gpa_units"]

    for course in remaining_courses(courses):
        grade = assumed.get(course["code"])
        if grade is None:
            continue
        value = grade_points(grade)
        if value is None:
            continue
        points += value * course["units"]
        units += course["units"]

    return round(points / units, 3) if units else 0.0


def scenarios(courses, varying, assumed=None, target=3.0):
    """Every combination of grades for the `varying` courses.

    Returns a list of (grades_dict, resulting_gpa, clears_target) sorted
    best first. `assumed` fixes grades for other courses first.
    """
    assumed = dict(assumed or {})
    rows = []
    for combo in product(LETTERS, repeat=len(varying)):
        grades = dict(zip(varying, combo))
        result = gpa_if(courses, {**assumed, **grades})
        rows.append((grades, result, result >= target))
    rows.sort(key=lambda r: -r[1])
    return rows


def next_ungraded_term(courses):
    """The earliest term that still has courses without a grade.

    Terms are strings like "Fall 2027", which do not sort alphabetically into
    calendar order, so this uses the order they first appear in the course
    list. Both data files are written chronologically.
    """
    seen = []
    for course in courses:
        if course["term"] not in seen:
            seen.append(course["term"])
    for term in seen:
        if any(c["term"] == term for c in remaining_courses(courses)):
            return term
    return None


def _report(courses):
    now = calculate_gpa(courses)
    remaining = remaining_gpa_units(courses)

    print("GPA PROJECTION")
    print()
    print(f"  now                   {now['gpa']:.3f}"
          f"   ({now['total_points']:.0f} points / {now['gpa_units']:.0f} units)")
    print(f"  units still to earn  {remaining:6.0f}")
    print(f"  units at graduation  {final_gpa_units(courses):6.0f}")
    print()
    print(f"  {'target':8}{'average needed':>16}   finishes at")
    print("  " + "-" * 46)
    for target in (3.00, 3.10, 3.20, 3.30):
        need = average_needed(courses, target)
        if need is None:
            print(f"  {target:<8}{'not reachable':>16}")
        else:
            print(f"  {target:<8}{need:>16.3f}   {target:.2f}")
    print(f"  {'ceiling':8}{4.0:>16.3f}   {ceiling(courses):.3f}")
    print()

    term = next_ungraded_term(courses)
    if term is None:
        print("Nothing left to grade.")
        return

    this_term = [c for c in remaining_courses(courses) if c["term"] == term]
    later = [c for c in remaining_courses(courses) if c["term"] != term]

    # Vary the two heaviest courses and assume A in the rest, because the
    # big ones are where the outcome is actually decided.
    by_weight = sorted(this_term, key=lambda c: -c["units"])
    varying = [c["code"] for c in by_weight[:2]]
    fixed = {c["code"]: "A" for c in by_weight[2:]}

    print(f"END OF {term.upper()}")
    if fixed:
        print(f"  assuming A in {', '.join(sorted(fixed))}")
    print(f"  ({len(later)} later courses stay ungraded)")
    print()
    print(f"  {varying[0]:10}{varying[1] if len(varying) > 1 else '':10}"
          f"{'cumulative':>12}   verdict")
    print("  " + "-" * 50)
    for grades, value, ok in scenarios(courses, varying, fixed, target=3.0):
        if any(g in "DE" for g in grades.values()):
            continue
        verdict = "clears 3.00" if ok else f"short by {3.0 - value:.3f}"
        cells = "".join(f"{grades[c]:10}" for c in varying)
        print(f"  {cells}{value:12.3f}   {verdict}")
    print()
    print(f"  {term} still to be graded: "
          f"{', '.join(c['code'] for c in this_term)}")


if __name__ == "__main__":
    courses, source = load_courses()
    print(f"source: {source}")
    print()
    _report(courses)
