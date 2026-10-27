"""Checks tracker.py and projection.py. Run with:  python check.py

These assertions are pinned to the SAMPLE data in data.py, deliberately and
always. They do not follow my_data.py, because a test suite whose expected
values move when you edit your own record is not a test suite.
"""

import sys

from data import COURSES, REQUIREMENTS
import projection
import tracker

results = []


def check(name, got, want, note=""):
    ok = abs(got - want) < 0.001 if isinstance(want, float) else got == want
    results.append((ok, name, f"got {got}, want {want}", note))


# ----------------------------------------------------- grade points

check("grade_points('A')", tracker.grade_points("A"), 4.0)
check("grade_points('E')", tracker.grade_points("E"), 0.0,
      "an E is zero points, not None - it still drags the average down")
check("grade_points('S') is None", tracker.grade_points("S") is None, True,
      "satisfactory earns units but no grade points")
check("grade_points(None) is None", tracker.grade_points(None) is None, True)


# -------------------------------------------- where the student is now

check("count_courses", tracker.count_courses(COURSES), 15)
check("earned_units", tracker.earned_units(COURSES), 50.0,
      "includes the 1-unit S grade, excludes the failed CHEM 102 attempt")
check("completed_upper_division_units",
      tracker.completed_upper_division_units(COURSES), 11.0)
check("completed_major_units", tracker.completed_major_units(COURSES), 20.0)
check("completed_major_upper_division_units",
      tracker.completed_major_upper_division_units(COURSES), 11.0)

gpa = tracker.calculate_gpa(COURSES)
check("gpa total_points", gpa["total_points"], 153.0)
check("gpa units", gpa["gpa_units"], 49.0,
      "50 earned minus the 1-unit S grade")
check("cumulative GPA", gpa["gpa"], 3.122)


# ------------------------------------------------ where the plan lands

check("planned_total_units", tracker.planned_total_units(COURSES), 107.0)
check("planned_upper_division_units",
      tracker.planned_upper_division_units(COURSES), 46.0)
check("planned_major_units", tracker.planned_major_units(COURSES), 51.0)
check("planned_major_upper_division_units",
      tracker.planned_major_upper_division_units(COURSES), 42.0)
check("planned_elective_units", tracker.planned_elective_units(COURSES), 25.0)
check("planned_gen_ed_units", tracker.planned_gen_ed_units(COURSES), 38.0)

# General education is an attribute, not a category, so a course can count
# toward the major AND satisfy a GE requirement from the same units. BIOL 101
# is the case to protect: Foundation Biology, and general education too.
biol = [c for c in COURSES if c["code"] == "BIOL 101"][0]
check("BIOL 101 is a major course", tracker.is_major(biol), True)
check("BIOL 101 is also general education", tracker.is_gen_ed(biol), True,
      "if these stop being independent, GE under-counts again")
check("its units are counted in both pools",
      biol["units"] <= tracker.planned_major_units(COURSES)
      and biol["units"] <= tracker.planned_gen_ed_units(COURSES), True)


# ------------------------------- the sample plan is short, on purpose

# A sample where everything passes would not show the tool doing anything.
# This student is 13 units short overall, so the report prints both PASS and
# SHORT. This assertion exists so nobody later "fixes" the sample and quietly
# removes the demonstration.
check("sample is short on total units",
      tracker.planned_total_units(COURSES) < REQUIREMENTS["total_units"], True,
      "deliberate: 107 against 120")


# ------------------------------------------------------ the decoy course

# EPID 309 is upper division and looks like an elective. It is categorised
# Other Upper Division, so it must not count toward the elective requirement.
# If this ever flips, planned_elective_units silently overstates by 3 units.
epid = [c for c in COURSES if c["code"] == "EPID 309"][0]
check("EPID 309 is not a Major Elective",
      epid["category"] != "Major Elective", True)
check("EPID 309 still counts as upper division",
      epid["upper_division"], True,
      "it is not an elective, but it is still a 300-level course")


# ---------------------------------------------------------- projection

check("remaining_gpa_units", projection.remaining_gpa_units(COURSES), 57.0)
check("final_gpa_units", projection.final_gpa_units(COURSES), 106.0,
      "49 banked plus 57 to come")
check("average_needed(3.00)", projection.average_needed(COURSES, 3.00), 2.895)
check("average_needed(3.20)", projection.average_needed(COURSES, 3.20), 3.267)
check("average_needed(3.90) is impossible",
      projection.average_needed(COURSES, 3.90) is None, True,
      "straight A grades would still not reach 3.90, so return None "
      "rather than a number above 4.0")
check("ceiling", projection.ceiling(COURSES), 3.594,
      "straight A grades from here")

all_a = {c["code"]: "A" for c in projection.remaining_courses(COURSES)}
check("gpa_if with straight A matches the ceiling",
      projection.gpa_if(COURSES, all_a), projection.ceiling(COURSES))
check("gpa_if with no assumptions leaves the GPA unchanged",
      projection.gpa_if(COURSES, {}), gpa["gpa"])


# -------------------------------------------------------------- output

print()
print("  " + "-" * 74)
for ok, name, detail, note in results:
    print(f"  {'PASS' if ok else 'FAIL'}  {name:42} {detail}")
    if note and not ok:
        print(f"        ^ {note}")
print("  " + "-" * 74)

bad = sum(1 for r in results if not r[0])
print(f"  {len(results) - bad} passing, {bad} failing")
print()

if bad:
    sys.exit(1)
