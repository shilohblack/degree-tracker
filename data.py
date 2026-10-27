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
  category        which requirement pool it belongs to
  excluded        True only for a repeat removed from the record
"""

COURSES = [
    {"code": "ENGL 101", "title": "Composition I", "units": 3, "term": "Fall Year 1",
     "grade": "A", "upper_division": False, "category": "Gen Ed", "excluded": False},
    {"code": "MATH 110", "title": "Precalculus", "units": 3, "term": "Fall Year 1",
     "grade": "B", "upper_division": False, "category": "Foundation Math", "excluded": False},
    {"code": "BIOL 101", "title": "Introductory Biology I", "units": 4, "term": "Fall Year 1",
     "grade": "B", "upper_division": False, "category": "Foundation Biology", "excluded": False},
    {"code": "CHEM 101", "title": "General Chemistry I", "units": 4, "term": "Fall Year 1",
     "grade": "C", "upper_division": False, "category": "Foundation Chemistry", "excluded": False},
    {"code": "ENGL 102", "title": "Composition II", "units": 3, "term": "Spring Year 1",
     "grade": "B", "upper_division": False, "category": "Gen Ed", "excluded": False},
    {"code": "BIOL 102", "title": "Introductory Biology II", "units": 4, "term": "Spring Year 1",
     "grade": "B", "upper_division": False, "category": "Foundation Biology", "excluded": False},
    {"code": "CHEM 102", "title": "General Chemistry II (1st attempt)", "units": 4, "term": "Spring Year 1",
     "grade": "E", "upper_division": False, "category": "Foundation Chemistry", "excluded": True},
    {"code": "SEMR 100", "title": "First Year Seminar", "units": 1, "term": "Spring Year 1",
     "grade": "S", "upper_division": False, "category": "Major Core", "excluded": False},
    {"code": "CHEM 102", "title": "General Chemistry II (retake)", "units": 4, "term": "Fall Year 2",
     "grade": "B", "upper_division": False, "category": "Foundation Chemistry", "excluded": False},
    {"code": "CSCI 200", "title": "Programming Fundamentals", "units": 4, "term": "Fall Year 2",
     "grade": "A", "upper_division": False, "category": "Foundation CS", "excluded": False},
    {"code": "STAT 150", "title": "Introductory Statistics", "units": 3, "term": "Fall Year 2",
     "grade": "A", "upper_division": False, "category": "Foundation CS", "excluded": False},
    {"code": "HIST 120", "title": "World History", "units": 3, "term": "Fall Year 2",
     "grade": "C", "upper_division": False, "category": "Gen Ed", "excluded": False},
    {"code": "GENE 310", "title": "Genetics", "units": 4, "term": "Spring Year 2",
     "grade": "B", "upper_division": True, "category": "Major Core", "excluded": False},
    {"code": "EVOL 335", "title": "Evolutionary Biology", "units": 4, "term": "Spring Year 2",
     "grade": "B", "upper_division": True, "category": "Major Core", "excluded": False},
    {"code": "DATA 320", "title": "Data Visualization", "units": 3, "term": "Spring Year 2",
     "grade": "A", "upper_division": True, "category": "Major Core", "excluded": False},
    {"code": "PHIL 140", "title": "Introduction to Ethics", "units": 3, "term": "Spring Year 2",
     "grade": "B", "upper_division": False, "category": "Gen Ed", "excluded": False},
    {"code": "BSTA 376", "title": "Introduction to Biostatistics", "units": 3, "term": "Fall Year 3",
     "grade": None, "upper_division": True, "category": "Biostatistics", "excluded": False},
    {"code": "ORGC 241", "title": "Organic Chemistry I", "units": 3, "term": "Fall Year 3",
     "grade": None, "upper_division": False, "category": "Foundation Chemistry", "excluded": False},
    {"code": "ORGC 243", "title": "Organic Chemistry I Lab", "units": 1, "term": "Fall Year 3",
     "grade": None, "upper_division": False, "category": "Foundation Chemistry", "excluded": False},
    {"code": "DATA 321", "title": "Data Mining", "units": 3, "term": "Fall Year 3",
     "grade": None, "upper_division": True, "category": "Data Course", "excluded": False},
    {"code": "BINF 340", "title": "Sequence Analysis", "units": 3, "term": "Fall Year 3",
     "grade": None, "upper_division": True, "category": "Major Elective", "excluded": False},
    {"code": "ARTS 150", "title": "Art Appreciation", "units": 3, "term": "Fall Year 3",
     "grade": None, "upper_division": False, "category": "Gen Ed", "excluded": False},
    {"code": "ORGC 242", "title": "Organic Chemistry II", "units": 3, "term": "Spring Year 3",
     "grade": None, "upper_division": False, "category": "Foundation Chemistry", "excluded": False},
    {"code": "ORGC 244", "title": "Organic Chemistry II Lab", "units": 1, "term": "Spring Year 3",
     "grade": None, "upper_division": False, "category": "Foundation Chemistry", "excluded": False},
    {"code": "MCBI 410", "title": "Cell Biology", "units": 3, "term": "Spring Year 3",
     "grade": None, "upper_division": True, "category": "Major Elective", "excluded": False},
    {"code": "EPID 309", "title": "Introduction to Epidemiology", "units": 3, "term": "Spring Year 3",
     "grade": None, "upper_division": True, "category": "Other Upper Division", "excluded": False},
    {"code": "SPAN 101", "title": "Elementary Spanish I", "units": 4, "term": "Spring Year 3",
     "grade": None, "upper_division": False, "category": "Gen Ed", "excluded": False},
    {"code": "BIOC 384", "title": "Biochemistry", "units": 3, "term": "Fall Year 4",
     "grade": None, "upper_division": True, "category": "Major Elective", "excluded": False},
    {"code": "MCBI 411", "title": "Molecular Biology", "units": 3, "term": "Fall Year 4",
     "grade": None, "upper_division": True, "category": "Major Elective", "excluded": False},
    {"code": "PHYS 320", "title": "Vertebrate Physiology", "units": 4, "term": "Fall Year 4",
     "grade": None, "upper_division": True, "category": "Major Elective", "excluded": False},
    {"code": "SOCI 160", "title": "Introduction to Sociology", "units": 3, "term": "Fall Year 4",
     "grade": None, "upper_division": False, "category": "Gen Ed", "excluded": False},
    {"code": "CAPS 301", "title": "General Education Capstone", "units": 1, "term": "Fall Year 4",
     "grade": None, "upper_division": True, "category": "Gen Ed", "excluded": False},
    {"code": "BIOC 385", "title": "Metabolic Biochemistry", "units": 3, "term": "Spring Year 4",
     "grade": None, "upper_division": True, "category": "Major Elective", "excluded": False},
    {"code": "BINF 450", "title": "Computational Genomics", "units": 3, "term": "Spring Year 4",
     "grade": None, "upper_division": True, "category": "Major Elective", "excluded": False},
    {"code": "NEUR 420", "title": "Neurobiology", "units": 3, "term": "Spring Year 4",
     "grade": None, "upper_division": True, "category": "Major Elective", "excluded": False},
    {"code": "SPAN 102", "title": "Elementary Spanish II", "units": 4, "term": "Spring Year 4",
     "grade": None, "upper_division": False, "category": "Gen Ed", "excluded": False},
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

# Categories that count toward the major-units requirement.
MAJOR_CATEGORIES = ["Foundation Biology", "Major Core", "Data Course",
                    "Major Elective", "Biostatistics"]
