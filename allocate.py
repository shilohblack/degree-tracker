"""Deciding which requirement each course fills.

Most courses can only fill one named requirement, so there is nothing to
decide. Some can fill more than one, and then the choice matters: putting a
course in the wrong slot can leave another requirement short while a
perfectly good course sits in a pool that was already satisfied.

Real degree audits solve this by picking the assignment that satisfies the
most requirements. So does this.

A worked example from real data. ISTA 321 and ISTA 322 can both satisfy the
Data Course requirement, but only ISTA 321 appears on the approved elective
list. Assign ISTA 321 to Data Course and ISTA 322 has nowhere to go: three
elective units vanish. Assign ISTA 322 to Data Course instead and ISTA 321
counts as an elective. Same two courses, same term, three units different.
"""

from itertools import product


def ambiguous(courses):
    """Courses that could fill more than one named requirement."""
    return [c for c in courses if len(c["pools"]) > 1]


def resolve(courses, choices):
    """Return the course list with every course pinned to one pool.

    `choices` maps a course code to the pool it has been assigned. Courses
    with a single option keep it. Courses with none get None, meaning they
    count toward totals and general education but fill no named requirement.
    """
    out = []
    for course in courses:
        pinned = dict(course)
        pools = course["pools"]
        if len(pools) == 1:
            pinned["pool"] = pools[0]
        elif len(pools) > 1:
            pinned["pool"] = choices.get(course["code"], pools[0])
        else:
            pinned["pool"] = None
        out.append(pinned)
    return out


def best(courses, score):
    """Try every assignment of the ambiguous courses and keep the best.

    `score` takes the resolved course list and returns a tuple, higher being
    better. Keeping it a callback means this module knows nothing about
    degrees, requirements or units.

    Returns (resolved_courses, choices, score).

    The search is exhaustive, which is fine because it is exponential only in
    the number of genuinely ambiguous courses, and that number is tiny. If it
    ever is not, this is the function to replace.
    """
    contested = ambiguous(courses)
    if not contested:
        resolved = resolve(courses, {})
        return resolved, {}, score(resolved)

    codes = [c["code"] for c in contested]
    options = [c["pools"] for c in contested]

    winner = None
    for combo in product(*options):
        choices = dict(zip(codes, combo))
        resolved = resolve(courses, choices)
        value = score(resolved)
        if winner is None or value > winner[2]:
            winner = (resolved, choices, value)
    return winner


def explain(courses, choices):
    """Lines describing each decision the allocator made."""
    lines = []
    for course in ambiguous(courses):
        taken = choices.get(course["code"])
        rejected = [p for p in course["pools"] if p != taken]
        lines.append(
            f"{course['code']} -> {taken}"
            f"   (could also have filled {', '.join(rejected)})"
        )
    return lines
