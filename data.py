"""Sample course data for a fictional BS Bioinformatics student.

This is NOT real student data. It is synthetic, but it keeps every
structural edge case that makes the logic interesting:

  * an excluded repeat   CHEM 102 was failed, retaken, and the first
                         attempt removed from the record entirely
  * an S grade           SEMR 100 earns units but no grade points
  * ungraded courses     everything from Year 3 onward
  * a decoy elective     EPID 309 is upper division and looks like an
                         elective, but its category says otherwise, so it
                         must not count toward the elective requirement

To run the tracker against your own record, copy this file to my_data.py
and edit it. my_data.py is gitignored and takes precedence automatically.

Keys on a course:
  code            course code
  units           units it is worth
  term            when it is taken
  grade           "A" to "E", "S" for satisfactory, or None if ungraded
  upper_division  True for 300 and 400 level
  pools           which named major requirements this course may fill.
                  Usually one. More than one means the allocator has a
                  genuine choice to make. Empty means it counts toward
                  totals and general education only.
  excluded        True only for a repeat removed from the record
  gen_ed          True if it carries a general education designation.
                  Independent of category: a course can be Foundation
                  Biology AND general education from the same units.
"""

COURSES = [
    {"code": "ENGL 101", "title": "Composition I", "units": 3, "term": "Fall Year 1",
     "grade": "A", "upper_division": False, "pools": [], "excluded": False, "gen_ed": True},
    {"code": "MATH 110", "title": "Precalculus", "units": 3, "term": "Fall Year 1",
     "grade": "B", "upper_division": False, "pools": ['Foundation Math'], "excluded": False, "gen_ed": True},
    {"code": "BIOL 101", "title": "Introductory Biology I", "units": 4, "term": "Fall Year 1",
     "grade": "B", "upper_division": False, "pools": ['Foundation Biology'], "excluded": False, "gen_ed": True},
    {"code": "CHEM 101", "title": "General Chemistry I", "units": 4, "term": "Fall Year 1",
     "grade": "C", "upper_division": False, "pools": ['Foundation Chemistry'], "excluded": False, "gen_ed": False},
    {"code": "ENGL 102", "title": "Composition II", "units": 3, "term": "Spring Year 1",
     "grade": "B", "upper_division": False, "pools": [], "excluded": False, "gen_ed": True},
    {"code": "BIOL 102", "title": "Introductory Biology II", "units": 4, "term": "Spring Year 1",
     "grade": "B", "upper_division": False, "pools": ['Foundation Biology'], "excluded": False, "gen_ed": False},
    {"code": "CHEM 102", "title": "General Chemistry II (1st attempt)", "units": 4, "term": "Spring Year 1",
     "grade": "E", "upper_division": False, "pools": ['Foundation Chemistry'], "excluded": True, "gen_ed": False},
    {"code": "SEMR 100", "title": "First Year Seminar", "units": 1, "term": "Spring Year 1",
     "grade": "S", "upper_division": False, "pools": ['Major Core'], "excluded": False, "gen_ed": True},
    {"code": "CHEM 102", "title": "General Chemistry II (retake)", "units": 4, "term": "Fall Year 2",
     "grade": "B", "upper_division": False, "pools": ['Foundation Chemistry'], "excluded": False, "gen_ed": False},
    {"code": "CSCI 200", "title": "Programming Fundamentals", "units": 4, "term": "Fall Year 2",
     "grade": "A", "upper_division": False, "pools": ['Foundation CS'], "excluded": False, "gen_ed": False},
    {"code": "STAT 150", "title": "Introductory Statistics", "units": 3, "term": "Fall Year 2",
     "grade": "A", "upper_division": False, "pools": ['Foundation CS'], "excluded": False, "gen_ed": True},
    {"code": "HIST 120", "title": "World History", "units": 3, "term": "Fall Year 2",
     "grade": "C", "upper_division": False, "pools": [], "excluded": False, "gen_ed": True},
    {"code": "GENE 310", "title": "Genetics", "units": 4, "term": "Spring Year 2",
     "grade": "B", "upper_division": True, "pools": ['Major Core'], "excluded": False, "gen_ed": False},
    {"code": "EVOL 335", "title": "Evolutionary Biology", "units": 4, "term": "Spring Year 2",
     "grade": "B", "upper_division": True, "pools": ['Major Core'], "excluded": False, "gen_ed": False},
    {"code": "DATA 320", "title": "Data Visualization", "units": 3, "term": "Spring Year 2",
     "grade": "A", "upper_division": True, "pools": ['Major Core'], "excluded": False, "gen_ed": False},
    {"code": "PHIL 140", "title": "Introduction to Ethics", "units": 3, "term": "Spring Year 2",
     "grade": "B", "upper_division": False, "pools": [], "excluded": False, "gen_ed": True},
    {"code": "BSTA 376", "title": "Introduction to Biostatistics", "units": 3, "term": "Fall Year 3",
     "grade": None, "upper_division": True, "pools": ['Biostatistics'], "excluded": False, "gen_ed": False},
    {"code": "ORGC 241", "title": "Organic Chemistry I", "units": 3, "term": "Fall Year 3",
     "grade": None, "upper_division": False, "pools": ['Foundation Chemistry'], "excluded": False, "gen_ed": False},
    {"code": "ORGC 243", "title": "Organic Chemistry I Lab", "units": 1, "term": "Fall Year 3",
     "grade": None, "upper_division": False, "pools": ['Foundation Chemistry'], "excluded": False, "gen_ed": False},
    {"code": "DATA 321", "title": "Data Mining", "units": 3, "term": "Fall Year 3",
     "grade": None, "upper_division": True, "pools": ['Data Course', 'Major Elective'], "excluded": False, "gen_ed": False},
    {"code": "BINF 340", "title": "Sequence Analysis", "units": 3, "term": "Fall Year 3",
     "grade": None, "upper_division": True, "pools": ['Major Core', 'Major Elective'], "excluded": False, "gen_ed": False},
    {"code": "ARTS 150", "title": "Art Appreciation", "units": 3, "term": "Fall Year 3",
     "grade": None, "upper_division": False, "pools": [], "excluded": False, "gen_ed": True},
    {"code": "ORGC 242", "title": "Organic Chemistry II", "units": 3, "term": "Spring Year 3",
     "grade": None, "upper_division": False, "pools": ['Foundation Chemistry'], "excluded": False, "gen_ed": False},
    {"code": "ORGC 244", "title": "Organic Chemistry II Lab", "units": 1, "term": "Spring Year 3",
     "grade": None, "upper_division": False, "pools": ['Foundation Chemistry'], "excluded": False, "gen_ed": False},
    {"code": "MCBI 410", "title": "Cell Biology", "units": 3, "term": "Spring Year 3",
     "grade": None, "upper_division": True, "pools": ['Major Elective'], "excluded": False, "gen_ed": False},
    {"code": "EPID 309", "title": "Introduction to Epidemiology", "units": 3, "term": "Spring Year 3",
     "grade": None, "upper_division": True, "pools": [], "excluded": False, "gen_ed": False},
    {"code": "SPAN 101", "title": "Elementary Spanish I", "units": 4, "term": "Spring Year 3",
     "grade": None, "upper_division": False, "pools": [], "excluded": False, "gen_ed": True},
    {"code": "BIOC 384", "title": "Biochemistry", "units": 3, "term": "Fall Year 4",
     "grade": None, "upper_division": True, "pools": ['Major Elective'], "excluded": False, "gen_ed": False},
    {"code": "MCBI 411", "title": "Molecular Biology", "units": 3, "term": "Fall Year 4",
     "grade": None, "upper_division": True, "pools": ['Major Elective'], "excluded": False, "gen_ed": False},
    {"code": "PHYS 320", "title": "Vertebrate Physiology", "units": 4, "term": "Fall Year 4",
     "grade": None, "upper_division": True, "pools": ['Major Elective'], "excluded": False, "gen_ed": False},
    {"code": "SOCI 160", "title": "Introduction to Sociology", "units": 3, "term": "Fall Year 4",
     "grade": None, "upper_division": False, "pools": [], "excluded": False, "gen_ed": True},
    {"code": "CAPS 301", "title": "General Education Capstone", "units": 1, "term": "Fall Year 4",
     "grade": None, "upper_division": True, "pools": [], "excluded": False, "gen_ed": True},
    {"code": "BIOC 385", "title": "Metabolic Biochemistry", "units": 3, "term": "Spring Year 4",
     "grade": None, "upper_division": True, "pools": ['Major Elective'], "excluded": False, "gen_ed": False},
    {"code": "BINF 450", "title": "Computational Genomics", "units": 3, "term": "Spring Year 4",
     "grade": None, "upper_division": True, "pools": ['Major Elective'], "excluded": False, "gen_ed": False},
    {"code": "NEUR 420", "title": "Neurobiology", "units": 3, "term": "Spring Year 4",
     "grade": None, "upper_division": True, "pools": ['Major Elective'], "excluded": False, "gen_ed": False},
    {"code": "SPAN 102", "title": "Elementary Spanish II", "units": 4, "term": "Spring Year 4",
     "grade": None, "upper_division": False, "pools": [], "excluded": False, "gen_ed": True},
]

# Units required to graduate.
REQUIREMENTS = {
    "total_units": 120,
    "upper_division": 42,
    "major_units": 50,
    "major_upper_division": 42,
    "major_electives": 23,
    "gen_ed": 32,
}

# Requirements counted in COURSES rather than units. The allocator has to
# score these too, otherwise it will happily move the only course that can
# fill one of them into a pool that was already satisfied.
COURSE_REQUIREMENTS = {
    "Data Course": 1,
    "Major Core": 5,
}

# Pools that count toward the major-units requirement.
MAJOR_POOLS = ["Foundation Biology", "Major Core", "Data Course",
               "Major Elective", "Biostatistics"]
