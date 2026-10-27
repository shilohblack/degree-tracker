# Degree Tracker

Checks a degree plan against graduation requirements and projects the GPA
forward. Written for a BS Bioinformatics programme, but the requirement
pools are data, not code, so it adapts.

It answers two separate questions about the same course list:

- **Where am I now?** The `completed_*` functions, from posted grades only.
- **Where does the plan land?** The `planned_*` functions, which include
  courses not taken yet.

Most degree calculators only answer the first. The second is the one that
tells you whether you graduate.

## Why it exists

A real planning error prompted it. Four electives were chosen from a list of
courses *available online* rather than the list the degree audit actually
*accepts*. Twelve units would have counted for nothing, and nobody would
have found out until the final audit.

So the central rule here is that **a course's `category` is the only thing
that decides which requirement pools it counts toward**. There is
deliberately no second list of approved course codes. Two lists can drift
apart, and a course quietly dropping out of one of them is exactly the bug
this program exists to catch.

The sample data includes `EPID 309` as a decoy: upper division, looks like an
elective, categorised `Other Upper Division`. It must not count toward the
elective requirement, and a test asserts it stays that way.

## Running it

```
python check.py        # 41 assertions
python tracker.py      # requirement report
python projection.py   # GPA projection
```

Against the bundled sample:

```
requirement                 earned  planned  needed   status
------------------------------------------------------------
total units                     50      107     120   SHORT
upper division units            11       46      42   PASS
major units                     20       51      50   PASS
major upper division            11       42      42   PASS
major elective units             0       25      23   PASS
general education units         12       27      32   SHORT
```

```
GPA PROJECTION

  now                   3.122   (153 points / 49 units)
  units still to earn      57
  units at graduation     106

  target    average needed   finishes at
  3.0                2.895   3.00
  3.2                3.267   3.20
  ceiling            4.000   3.594
```

The sample student is **deliberately 13 units short** overall and 5 short on
general education, so the report demonstrates both outcomes. Two assertions
in `check.py` exist purely to stop anyone "fixing" that and removing the
demonstration.

## Using your own record

Copy `data.py` to `my_data.py` and edit it. `my_data.py` is gitignored and
takes precedence automatically, so `tracker.py` and `projection.py` will use
it while `check.py` stays pinned to the sample.

A test suite whose expected values move when you edit your own data is not a
test suite.

## Files

| File | |
| --- | --- |
| `data.py` | Sample courses and the requirements. Synthetic. |
| `tracker.py` | Requirement logic and the report. |
| `projection.py` | GPA projection and grade scenarios. |
| `allocate.py` | Decides which requirement a contested course fills. |
| `check.py` | 41 assertions, pinned to the sample data. |

## The interesting parts

**GPA has three traps**, all represented in the sample: a repeat the
registrar removed from the record entirely, an S grade that earns units but
carries no grade points, and courses with no grade yet. All three must stay
out of the fraction, and two of them must stay out of *both* the numerator
and the denominator.

**`average_needed(target)` returns `None`** when a target cannot be reached
even with straight A grades, rather than printing a number above 4.0.

**`scenarios(varying, assumed)`** enumerates every grade combination for the
courses you name. The report calls it with the two heaviest courses in the
next ungraded term, but you can point it at any list of codes.

## Pools are not mutually exclusive

A course's `category` decides its major pool, but general education is a
separate boolean attribute, because real audits let one course satisfy both
from the same units. `BIOL 101` is Foundation Biology *and* general
education: its four units count toward the 50-unit major requirement and the
32-unit general education requirement at once.

Getting this wrong is an easy way to under-count by ten units or more and
conclude you are short when you are not. Three assertions guard it.

## Courses that could fill more than one requirement

A course lists the pools it is *eligible* for. Most list one, so there is
nothing to decide. Some list two, and then the choice matters.

The real case: `ISTA 321` and `ISTA 322` can both satisfy the Data Course
requirement, but only `ISTA 321` is on the approved elective list. Put
`ISTA 321` in the Data Course slot and `ISTA 322` has nowhere to go, losing
three elective units. Put `ISTA 322` there instead and both count.

`allocate.py` tries every assignment of the contested courses and keeps the
one that satisfies the most requirements, breaking ties on smallest total
shortfall. The search is exhaustive, which is fine because it is exponential
only in the number of genuinely contested courses, and that is a handful.

Two things it gets right that a greedy version does not:

**Surplus counts for nothing.** Banking three spare elective units is worth
less than filling a requirement you cannot graduate without. Score surplus
as credit and the allocator will cheerfully strip the only course that can
satisfy a requirement in order to pad a pool that was already full.

**Course-count requirements are scored too.** Data Course needs one course
and Major Core needs five. An allocator that only knows about unit totals
will empty those to feed the unit pools, and nothing will notice.

The report prints both kinds, so an unfilled requirement is visible rather
than implied by a number being lower than expected.
