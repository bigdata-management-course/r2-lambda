"""Self-checks: python3 check.py [c1-c5 h1-h5]  (default: all).

c = in class, h = at home. Exit status is 0 even when checks fail; it is 1 only if observations.py
cannot be imported.
"""
import hashlib
import json
import sys
from pathlib import Path

import observations as obs

HERE = Path(__file__).resolve().parent
GROUPS = {"in class:": "c1 c2 c3 c4 c5", "at home:": "h1 h2 h3 h4 h5"}
# Digests of the correct observations on recording.jsonl.gz.
EXPECTED = {
    "V2_ROW": "5d8f6cce532a",
    "FIRST_REAL_COUNT": "e629fa6598d7",
    "BATCH_PAGES": "82d2cacdab92",
    "V2_PAGES": "d6f0c71ef0c8",
    "LATE_EVENTS": "434c9b5ae514",
    "MOVED": "5966abd0cbfc",
    "SEAM_SEEN": "38206b956d53",
    "SEAM_TOTAL": "3c54e95a9ac8",
    "BOT_SHARE": "717cb9fead9e",
    "ENWIKI_KEPT": "c8bcad7f2864",
    "OFFSET_1000": "b59c10be63a2",
    "LEON_NO_BUG": "6b51d431df5d",
    "LATE_20": "6b51d431df5d",
    "BATCH_LAG4": "6b51d431df5d",
    "NEW_KEPT": "2c7d5490e605",
    "NEW_ENWIKI": "e29c9c180c62",
}
# First 12 hex digits of the sha1 of the pristine files.
PRISTINE = {
    "core.py": "d9df2f839264",
    "recording.jsonl.gz": "7f79a84c6ac7",
}
CHECKS = {
    "c1": ["V2_ROW", "FIRST_REAL_COUNT"], "c2": ["BATCH_PAGES", "V2_PAGES"], "c3": ["LATE_EVENTS", "MOVED"],
    "c4": ["SEAM_SEEN", "SEAM_TOTAL"], "c5": ["BOT_SHARE", "ENWIKI_KEPT"],
    "h1": ["OFFSET_1000"], "h2": ["LEON_NO_BUG"], "h3": ["LATE_20"], "h4": ["BATCH_LAG4"],
    "h5": ["NEW_KEPT", "NEW_ENWIKI"],
}


def sha1(data):
    return hashlib.sha1(data).hexdigest()[:12]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()[:12]


def observed(name):
    value = getattr(obs, name)
    if value is None:
        print(f"  {name}: not filled in yet")
        return False
    ok = digest(value) == EXPECTED[name]
    print(f"  {name} = {value!r}: {'ok' if ok else 'WRONG'}")
    return ok


def warn_if_changed():
    """The in-class edits must be undone, or later numbers shift."""
    for name, sha in PRISTINE.items():
        data = (HERE / name).read_bytes()
        if name.endswith(".py"):
            data = data.replace(b"\r\n", b"\n")
        if sha1(data) != sha:
            print(f"WARNING: {name} differs from the original: undo your edit with 'git checkout {name}'")


if __name__ == "__main__":
    every = " ".join(GROUPS.values()).split()
    wanted = sys.argv[1:] or every
    if not set(wanted) <= set(every):
        sys.exit("usage: python3 check.py [c1-c5 h1-h5]")
    warn_if_changed()
    res = {}
    for n in wanted:
        print(n)
        res[n] = all([observed(name) for name in CHECKS[n]])
    for label, group in GROUPS.items():
        row = [f"{n} {'PASS' if res[n] else 'FAIL'}" for n in group.split() if n in res]
        if row:
            print(f"{label:10}" + "  ".join(row))
