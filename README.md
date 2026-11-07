# Recitation 2: Lambda by hand

The code of Recitation 2: seven Lecture 2 terms (immutable master dataset, event vs. arrival time,
batch view, serving layer, speed layer, query merge, Kappa), each shown in `demo.py` and built in
about 120 lines of Python in `lam.py`. For each term you change one setting of the demo and record what you
see (terms 6 and 7 in class, 1-5 at home this time); then you answer new questions with the same tools. `worksheet.pdf` has
everything. Not graded.

## Setup

You need Python 3.8+ and git. No packages, no GitHub account: the repository is public.

```sh
git clone https://github.com/bigdata-management-course/r2-lambda.git
cd r2-lambda
python3 check.py      # first run also generates data/ (16.5 MB, a few seconds)
```

The last three lines must be:

```
in class: c1 FAIL  c2 FAIL  c3 FAIL  c4 FAIL  c5 FAIL  c6 FAIL  c7 FAIL
at home:  h1 FAIL  h2 FAIL  h3 FAIL  h4 FAIL  h5 FAIL  h6 FAIL  h7 FAIL
further:  g1 FAIL  g2 FAIL
```

`FAIL` only means "not filled in yet". On Windows use `py` or `python` instead of `python3`.
If `git clone` asks for a password, the URL has a typo. Without git, *Code → Download ZIP* works too.

## Working on an item

1. Make the change the slide or `worksheet.pdf` asks for (a setting in `demo.py`, once a line of
   `lam.py` or `gen.py`) and run the demo step, e.g. `python3 demo.py 2`.
2. Write the value you saw into `observations.py`, then check it: `python3 check.py c2`
   (or `h1 h2`, or nothing for all). The checker compares digests and never shows the expected value.
3. Undo the change (`git checkout <file>` restores a file). `check.py` warns if `data/master` or
   `lam.py` still differs from the original.
4. Rerun `python3 check.py` and read its PASS/FAIL lines: that is your feedback. Your answers stay in
   your own copy; there is nothing to push or submit.

## Files

| File | What it is |
|---|---|
| `observations.py` | Your observations: one value per item. |
| `further.py` | Going further (optional): an idempotent speed layer and HyperLogLog. |
| `lam.py` | The architecture: master dataset, batch, serving, speed layer, query merge, Kappa replay. |
| `demo.py` | The instructor's demo, one step per term: `python3 demo.py 3`; `python3 demo.py` runs 1-7. |
| `gen.py` | Generates the master dataset into `data/master/` (fixed seed: everyone has the same data). |
| `check.py` | Self-checks: `python3 check.py [c1-c7 h1-h7 g1 g2 ...]`. |
| `worksheet.pdf` | Every item: what to change, what to run, what you should see, hints. |

To start over with the data, delete `data/` and rerun `python3 check.py`.
