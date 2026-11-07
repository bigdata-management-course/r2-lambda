"""A mini Lambda Architecture over the page-view master dataset (stdlib only)."""
import json
import os
import random
from collections import Counter, defaultdict
from pathlib import Path

DATA = Path(__file__).parent / "data"
MASTER, VIEWS = DATA / "master", DATA / "views"


def hour(ts):
    return ts[:13]  # "2026-10-26T14:03:27" -> "2026-10-26T14"


def url_hour(e):
    return (e["url"], hour(e["ts"]))


def arrivals():
    names = MASTER.glob("arrival=*.jsonl")
    return sorted(p.stem[len("arrival="):] for p in names)


def read_facts(since="", until="~"):
    """Facts that arrived in [since, until), in arrival order."""
    for a in arrivals():
        if since <= a < until:
            with open(MASTER / f"arrival={a}.jsonl") as f:
                for line in f:
                    yield a, json.loads(line)


# --- batch layer: recompute from ALL facts up to the horizon ---
def batch_view(until, key=url_hour):
    views, visitors = Counter(), defaultdict(set)
    for _, e in read_facts(until=until):
        k = key(e)
        views[k] += 1
        visitors[k].add(e["visitor"])
    return {"horizon": until, "views": views,
            "uniques": {k: len(v) for k, v in visitors.items()}}


# --- serving layer: bulk-load a whole view, then random reads ---
def publish(view, name="batch"):
    VIEWS.mkdir(parents=True, exist_ok=True)
    tmp = VIEWS / f"{name}.json.tmp"
    flat = {"horizon": view["horizon"]}
    for part in ("views", "uniques"):
        flat[part] = {"|".join(k): v for k, v in view[part].items()}
    tmp.write_text(json.dumps(flat))
    # Atomic rename: readers see old or new view, never half.
    os.replace(tmp, VIEWS / f"{name}.json")


class Serving:
    def __init__(self, name="batch"):
        d = json.loads((VIEWS / f"{name}.json").read_text())
        self.horizon, self.views = d["horizon"], d["views"]

    def get(self, url, h):
        return self.views.get(f"{url}|{h}", 0)


# --- speed layer: incremental, only facts the batch lacks ---
class Speed:
    def __init__(self, horizon):
        self.horizon = horizon
        # arrival hour -> (url, hour) -> views
        self.buckets = defaultdict(Counter)

    def on_event(self, arrival, e):
        if arrival >= self.horizon:
            self.buckets[arrival][url_hour(e)] += 1

    def advance(self, horizon):
        """Batch now covers all before `horizon`: forget it."""
        for a in [a for a in self.buckets if a < horizon]:
            del self.buckets[a]
        self.horizon = horizon

    def get(self, url, h, since=""):
        return sum(b[(url, h)] for a, b in self.buckets.items()
                   if a >= since)

    def view(self):
        return sum(self.buckets.values(), Counter())


# --- query: merge(batch view, real-time view) ---
def query(serving, speed, url, hours):
    # Skip buckets the view covers, even before advance().
    T = serving.horizon
    return {h: (serving.get(url, h), speed.get(url, h, since=T))
            for h in hours}


# --- Kappa: one stream job, reprocess by replaying the log ---
def replay(keep=None):
    job = Speed(horizon="")
    for a, e in read_facts():
        if keep is None or keep(e):
            job.on_event(a, e)
    return job.view()


# --- an at-least-once stream: redelivers some facts, as after a consumer crash ---
def deliver(since, until, dup=0.05, seed=7):
    rng, pending = random.Random(seed), []
    for a, e in read_facts(since, until):
        yield a, e
        if rng.random() < dup:
            pending.append((a, e))
        if pending and rng.random() < 0.5:
            yield pending.pop(0)
    yield from pending
