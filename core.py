"""The architecture in one file: stream source, master dataset, batch view, speed layer, query."""
import argparse
import calendar
import gzip
import http.client
import json
import sys
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

URL = "https://stream.wikimedia.org/v2/stream/recentchange"
AGENT = "bigdata-course-r2/1.0 (University of Haifa course; https://github.com/bigdata-management-course/r2-lambda)"
HERE = Path(__file__).resolve().parent
RECORDING = HERE / "recording.jsonl.gz"
MASTER = HERE / "data" / ("master-live" if "--live" in sys.argv else "master")


# --- the stream: live from Wikimedia, or the recording replayed -------------------------------

def stream(speed):
    """python3 <act>.py [--speed N] [--live]: the recording N times faster than real time, or live."""
    p = argparse.ArgumentParser()
    p.add_argument("--speed", type=float, default=speed, help="0 = as fast as possible")
    p.add_argument("--live", action="store_true", help="read stream.wikimedia.org instead")
    a = p.parse_args()
    return live() if a.live else replay(a.speed)


def live():
    """Events from Wikimedia, forever. Reconnects after errors, resuming where it left off."""
    last = None
    while True:
        headers = {"User-Agent": AGENT}
        if last:
            headers["Last-Event-ID"] = last
        try:
            with urllib.request.urlopen(urllib.request.Request(URL, headers=headers), timeout=60) as r:
                for raw in r:
                    line = raw.decode("utf-8").rstrip("\r\n")
                    if line.startswith("id: "):
                        last = line[4:]
                    elif line.startswith("data: "):
                        e = json.loads(line[6:])
                        if e["meta"].get("domain") != "canary":  # Wikimedia's own health probes
                            yield e
        except (OSError, http.client.HTTPException, ValueError) as err:
            print(f"stream: {err}; reconnecting in 5 s", file=sys.stderr)
            time.sleep(5)


def replay(speed, path=RECORDING):
    """The recorded events, paced by arrival time: speed 1 = real time, 0 = as fast as possible."""
    first = None
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            e = json.loads(line)
            if speed:
                first = first or (arrival(e), time.monotonic())
                wait = (arrival(e) - first[0]) / speed - (time.monotonic() - first[1])
                if wait > 0:
                    time.sleep(wait)
            yield e


def arrival(e):
    """Arrival time, unix seconds: when Wikimedia's Kafka received the event (meta.dt)."""
    dt = e["meta"]["dt"]  # "2026-11-07T15:00:00.123Z"
    return calendar.timegm(time.strptime(dt[:19], "%Y-%m-%dT%H:%M:%S")) + float("0" + dt[19:-1])


def minute(t):
    return int(t // 60)


def hhmm(m):
    return time.strftime("%H:%M", time.gmtime(m * 60))


def clock(t):
    return time.strftime("%H:%M:%S", time.gmtime(t))


def is_edit(e):
    """An edit or a new page of a Wikipedia article: what readers mean by a hot page."""
    return e["type"] in ("edit", "new") and e["server_name"].endswith(".wikipedia.org") and e["namespace"] == 0


def page(e):
    return e["wiki"] + ":" + e["title"]


def page_v2(e):
    return e["wiki"] + ":" + e.get("page", "")  # v2 "renamed" the field; the event has no "page"


# --- master dataset: raw events, one file per arrival minute, never rewritten -----------------

def fname(m):
    return time.strftime("arrival=%Y-%m-%dT%H:%M.jsonl", time.gmtime(m * 60))


class Collector:
    """Appends events to the file of the current arrival minute; closes it when the minute ends."""

    def __init__(self, folder=MASTER):
        folder.mkdir(parents=True, exist_ok=True)
        self.folder, self.m, self.f = folder, None, None

    def add(self, e):
        """Files e and returns its arrival minute. Kafka order is off by <1 s at times: such an
        event goes into the open file, so a closed file stays closed."""
        m = minute(arrival(e))
        if self.m is None or m > self.m:
            self.close()
            self.m = m
            self.done = self.folder / fname(m)
            self.tmp = self.done.with_suffix(".tmp")
            self.f = None if self.done.exists() else open(self.tmp, "w", encoding="utf-8")
        if self.f:
            self.f.write(json.dumps(e, ensure_ascii=False) + "\n")
        return self.m

    def close(self):
        if self.f:
            self.f.close()
            self.tmp.replace(self.done)  # a file appears complete or not at all
            self.f = None


def facts(until=None, folder=MASTER):
    """Every event in the closed files of arrival minutes before `until` (all if None)."""
    for p in sorted(folder.glob("arrival=*.jsonl")):
        if until is None or p.name < fname(until):
            with open(p, encoding="utf-8") as f:
                yield from map(json.loads, f)


# --- batch, speed, query -----------------------------------------------------------------------

def batch_view(T, key=page):
    """Recomputed from scratch from the master dataset: edits per page, of all that arrived before T."""
    return T, Counter(key(e) for e in filter(is_edit, facts(T)))


class Speed:
    """Counts per arrival minute, for the minutes the batch view does not cover yet."""

    def __init__(self, key=page):
        self.key, self.buckets = key, defaultdict(Counter)

    def add(self, e, m):
        self.buckets[m][self.key(e)] += 1

    def advance(self, T):
        """A batch view up to T is published: forget the minutes it now covers."""
        for m in [m for m in self.buckets if m < T]:
            del self.buckets[m]

    def view(self, since=None):
        out = Counter()
        for m, counts in self.buckets.items():
            if since is None or m >= since:
                out.update(counts)
        return out


def query(batch, speed):
    """Serving layer: batch view + speed view, merged per key."""
    T, view = batch
    total = Counter(view)
    total.update(speed.view(since=T))
    return total


# --- terminal output ---------------------------------------------------------------------------

def show(lines):
    """A refreshing screen on a terminal; one frame after the other when piped to a file."""
    if sys.stdout.isatty():
        print("\033[H\033[J", end="")
    print("\n".join(lines) + ("" if sys.stdout.isatty() else "\n"), flush=True)


def run(main):
    try:
        main()
    except KeyboardInterrupt:
        print()
