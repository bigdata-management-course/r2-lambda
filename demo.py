"""The instructor's demos, one per Lecture 2 concept: python3 demo.py [1-8 ...].

The default runs 1-7; step 8 is self-study.

"Your turn" asks you to edit the CAPITALISED settings of a step and run it again.
"""
import hashlib
import json
import sys
import time
from collections import Counter

import gen
import lam

D = gen.DAY
H = {h: f"{D}T{h:02}" for h in range(6, 17)}
URL = "/news/8812"


# 1. Immutable master dataset ------------------------------------------------
def step1():
    gen.generate()
    files = sorted(lam.MASTER.glob("*.jsonl"))
    n = sum(1 for _ in lam.read_facts())
    mb = sum(f.stat().st_size for f in files) / 1e6
    print(f"{len(files)} files, {n} facts, {mb:.1f} MB")
    for f in files[:2] + files[-1:]:
        sha = hashlib.sha1(f.read_bytes()).hexdigest()[:12]
        first = json.loads(f.read_text().split("\n")[0])
        print(f"  {f.name}  sha1 {sha}  first id {first['id']}")


# 2. Event time vs arrival time ----------------------------------------------
ARRIVAL = H[12]  # the arrival file to inspect


def step2():
    late = sum(1 for a, e in lam.read_facts() if lam.hour(e["ts"]) < a)
    print(f"late facts in the whole log: {late}")
    per_hour, earliest = {}, "~"
    for a, e in lam.read_facts(since=ARRIVAL, until=ARRIVAL + "~"):
        h = lam.hour(e["ts"])
        per_hour[h] = per_hour.get(h, 0) + 1
        earliest = min(earliest, e["ts"])
    late_here = sum(v for h, v in per_hour.items() if h < ARRIVAL)
    print(f"file arrival={ARRIVAL}, facts per event hour:")
    print(f"  {dict(sorted(per_hour.items()))}")
    print(f"  late: {late_here}, earliest event time: {earliest}")


# 3. Batch view: recompute from all facts ------------------------------------
HORIZON = H[12]
KEY = lam.url_hour  # how the view groups facts


def step3():
    t = time.perf_counter()
    v = lam.batch_view(until=HORIZON, key=KEY)
    dt = time.perf_counter() - t
    n = sum(v["views"].values())
    rows = len(v["views"])
    print(f"batch view up to {HORIZON}: {n} facts -> {rows} rows in {dt:.2f} s")
    for k, n in v["views"].most_common(3):
        print(f"  {k}  views={n}  uniques={v['uniques'][k]}")


# 4. Serving layer: publish a whole view, swap it atomically ---------
ASK = (URL, H[11])  # the key the dashboard reads


def step4():
    lam.publish(lam.batch_view(until=H[12]))
    s = lam.Serving()
    t = time.perf_counter()
    for _ in range(100_000):
        s.get(*ASK)
    us = (time.perf_counter() - t) / 100_000 * 1e6
    print(f"before: horizon {s.horizon}, get{ASK} = {s.get(*ASK)}  ({us:.2f} us/get)")
    lam.publish(lam.batch_view(until=H[14]))  # the next batch run swaps the file
    s = lam.Serving()
    print(f"after:  horizon {s.horizon}, get{ASK} = {s.get(*ASK)}")


# 5. Speed layer: incremental, only what the batch lacks ---------------------
UNTIL = H[14]
STREAM = lam.read_facts  # lam.deliver is an at-least-once stream


def step5():
    speed = lam.Speed(horizon=H[12])
    for i, (a, e) in enumerate(STREAM(H[12], UNTIL), 1):
        speed.on_event(a, e)
        if i % 10_000 == 0:
            print(f"  after {i:5} events: {URL} 12:00 = {speed.get(URL, H[12])}")
    total = sum(speed.view().values())
    buckets = [b[-2:] for b in sorted(speed.buckets)]
    print(f"speed layer: buckets {buckets}, {total} views counted")
    for h in (11, 12, 13):
        print(f"  {URL} {h}:00  realtime={speed.get(URL, H[h])}")
    return speed


# 6. Query = batch view + real-time view, split at the horizon ----------------
def show(title, serving, speed):
    print(title)
    rows = lam.query(serving, speed, URL, [H[h] for h in range(10, 14)])
    for h, (b, r) in rows.items():
        print(f"  {h[-2:]}:00  batch={b:5}  realtime={r:5}  total={b + r:5}")


def step6():
    lam.publish(lam.batch_view(until=H[12]))
    speed = lam.Speed(horizon=H[12])
    for a, e in lam.read_facts(H[12], H[14]):
        speed.on_event(a, e)
    show(f"query at 14:00, batch horizon {H[12]}", lam.Serving(), speed)
    lam.publish(lam.batch_view(until=H[14]))
    show(f"new view published (horizon {H[14]}), speed not advanced",
         lam.Serving(), speed)
    speed.advance(H[14])
    show("after speed.advance()", lam.Serving(), speed)


# 7. Kappa: reprocess by replaying the log through the stream job ----
KEEP = None  # job version 2: a function fact -> bool that keeps a fact


def step7():
    t = time.perf_counter()
    kappa = lam.replay(keep=KEEP)
    dt = time.perf_counter() - t
    batch = lam.batch_view(until="~")["views"]
    n, nb = sum(kappa.values()), sum(batch.values())
    print(f"replayed the log in {dt:.2f} s: {n} views, {nb - n} dropped by KEEP")
    print(f"equals the batch view: {kappa == batch}")


# 8. Self-study: human fault tolerance (depth for concept 1) ------------------
# Deployed at 12:00, drops the article id: /news/8812 -> /news
def buggy_url_hour(e):
    return (e["url"].rsplit("/", 1)[0] or "/", lam.hour(e["ts"]))


def step8():
    table = Counter()  # a mutable store: only the counters survive
    for a, e in lam.read_facts(until=H[14]):
        table[(buggy_url_hour if a >= H[12] else lam.url_hour)(e)] += 1
    truth = lam.batch_view(until=H[14])["views"]
    news = table[("/news", H[12])]
    print(f"{URL} 12:00  mutable store={table[(URL, H[12])]}  ('/news', 12:00)={news}")
    print(f"{URL} 12:00  recomputed from facts={truth[(URL, H[12])]}")


if __name__ == "__main__":
    for s in sys.argv[1:] or "1234567":
        print(f"--- step {s}")
        globals()[f"step{s}"]()
