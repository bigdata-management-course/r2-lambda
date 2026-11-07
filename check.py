"""Self-checks: python3 check.py [c1-c7 h1-h7 g1 g2 ...]  (default: all).

c = in class ("Your turn"), h = at home, g = going further. Exit status is 0 even when checks
fail; it is 1 only if observations.py or further.py cannot be imported.
"""
import hashlib
import json
import sys
import traceback
from pathlib import Path

import further
import gen
import lam
import observations as obs

GROUPS = {"in class:": "c1 c2 c3 c4 c5 c6 c7", "at home:": "h1 h2 h3 h4 h5 h6 h7", "further:": "g1 g2"}
H = {h: f"2026-10-26T{h:02}" for h in range(6, 17)}
# Digests of the correct observations on the generated dataset (gen.py, seed 2026).
EXPECTED = {
    "NEW_FIRST_ID": "0d41ae74bb90",
    "LATE_IN_08": "55f0124bb79f",
    "EARLIEST_IN_08": "6da77109d4cb",
    "REF_ROWS": "624b60c58c9d",
    "GOOGLE_10": "b8d4d60e7f9c",
    "HOME_13_BEFORE": "5feceb66ffc8",
    "HOME_13_AFTER": "c5012fb6613a",
    "DUPLICATES": "77459b9b941b",
    "NEWS_12_WITH_DUPS": "3849ba084da2",
    "DOUBLE_11": "0e3c49c57d4a",
    "BOT_VIEWS": "93e31df2f727",
    "STORE_NEWS_12": "70cc44b2ed0e",
    "MOST_LATE_FILE": "e8d1408853c0",
    "GOOGLE_SHARE_11": "26ccbceee7ef",
    "KEYS_AFTER_SWAP": "05798b5867fa",
    "LATE_11_IN_BUCKET_13": "8527a891e224",
    "LOST_BY_SPLIT": "ec7cdb832561",
    "V2_NEWS_11": "9eb2d543a0a3",
}
# First 12 hex digits of the sha1 of each pristine arrival file, and of lam.py.
MASTER_SHA1 = {
    "arrival=2026-10-26T08.jsonl": "f4c304aeb363",
    "arrival=2026-10-26T09.jsonl": "5cc28f6ecba2",
    "arrival=2026-10-26T10.jsonl": "966188b5d5cb",
    "arrival=2026-10-26T11.jsonl": "7d03cc699695",
    "arrival=2026-10-26T12.jsonl": "dc3268297093",
    "arrival=2026-10-26T13.jsonl": "8f8384a745ed",
    "arrival=2026-10-26T14.jsonl": "93e5aa6055e7",
    "arrival=2026-10-26T15.jsonl": "79c4dc830816",
}
LAM_SHA1 = "eaedf4f7506d"
CHECKS = {
    "c1": ["NEW_FIRST_ID"], "c2": ["LATE_IN_08", "EARLIEST_IN_08"], "c3": ["REF_ROWS", "GOOGLE_10"],
    "c4": ["HOME_13_BEFORE", "HOME_13_AFTER"], "c5": ["DUPLICATES", "NEWS_12_WITH_DUPS"],
    "c6": ["DOUBLE_11"], "c7": ["BOT_VIEWS"],
    "h1": ["STORE_NEWS_12"], "h2": ["MOST_LATE_FILE"], "h3": ["GOOGLE_SHARE_11"], "h4": ["KEYS_AFTER_SWAP"],
    "h5": ["LATE_11_IN_BUCKET_13"], "h6": ["LOST_BY_SPLIT"], "h7": ["V2_NEWS_11"],
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
    """The Your-turn edits to gen.py, lam.py and data/ must be undone, or later numbers shift."""
    files = {p.name: sha1(p.read_bytes()) for p in sorted(lam.MASTER.glob("*.jsonl"))}
    for name in sorted(set(files) - set(MASTER_SHA1)):
        print(f"WARNING: data/master/{name} is not part of the dataset: delete it")
    for name, sha in MASTER_SHA1.items():
        if files.get(name) != sha:
            print(f"WARNING: data/master/{name} is missing or changed: delete data/ and rerun check.py")
    text = Path(lam.__file__).read_text().replace("\r\n", "\n")
    if sha1(text.encode()) != LAM_SHA1:
        print("WARNING: lam.py differs from the original: undo your edit with 'git checkout lam.py'")


def g1():
    clean = lam.Speed(H[12])
    for a, e in lam.read_facts(H[12], H[14]):
        clean.on_event(a, e)
    stream = list(lam.deliver(H[12], H[14]))
    d = further.DedupSpeed(H[12])
    for a, e in stream:
        d.on_event(a, e)
    ok = d.view() == clean.view()
    print(f"  {len(stream) - 40000} duplicates delivered; counts exact: {ok}")
    d.advance(H[13])
    held = sum(len(s) for s in d.seen.values())
    print(f"  after advance({H[13][-2:]}): ids held = {held} (expected 20000)")
    return ok and held == 20000


def g2():
    facts = [e for _, e in lam.read_facts()]
    exact = {e["visitor"] for e in facts}
    hll = further.HLL()
    for e in facts:
        hll.add(e["visitor"])
    err = abs(hll.count() - len(exact)) / len(exact)
    print(f"  uniques: exact={len(exact)}  HLL={hll.count():.0f}  error={err:.2%}")
    print(f"  memory: HLL {len(hll.reg)} B vs exact set {sys.getsizeof(exact)} B (container only)")
    a, b, both = further.HLL(), further.HLL(), further.HLL()
    for e in facts:
        if lam.hour(e["ts"]) == H[10]:
            a.add(e["visitor"]), both.add(e["visitor"])
        elif lam.hour(e["ts"]) == H[11]:
            b.add(e["visitor"]), both.add(e["visitor"])
    merged = a.merge(b)
    print(f"  10:00 + 11:00: {a.count():.0f} + {b.count():.0f}, merged {merged.count():.0f},"
          f" built on both {both.count():.0f}")
    return err < 0.065 and merged.reg == both.reg


def run(name):
    print(name)
    if name in CHECKS:
        return all([observed(n) for n in CHECKS[name]])
    try:
        return bool(globals()[name]())
    except NotImplementedError:
        print("  not implemented yet")
    except Exception:  # one broken check must not hide the others' results
        traceback.print_exc(file=sys.stdout)
    return False


if __name__ == "__main__":
    gen.generate()  # no-op once data/ exists
    every = " ".join(GROUPS.values()).split()
    wanted = sys.argv[1:] or every
    if not set(wanted) <= set(every):
        sys.exit("usage: python3 check.py [c1-c7 h1-h7 g1 g2 ...]")
    warn_if_changed()
    res = {n: run(n) for n in wanted}
    for label, group in GROUPS.items():
        row = [f"{n} {'PASS' if res[n] else 'FAIL'}" for n in group.split() if n in res]
        if row:
            print(f"{label:10}" + "  ".join(row))
