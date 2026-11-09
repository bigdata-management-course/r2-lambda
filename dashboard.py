"""Act 3, Lambda: python3 dashboard.py [--speed N] [--live]. Batch view + speed view, refreshed live."""
from collections import Counter

import core

TOP = 8
BATCH_EVERY = 5  # minutes between two batch runs
BATCH_LAG = 2  # a batch view covers what arrived up to this many minutes ago
REFRESH = 20  # seconds of stream time between two frames


def main():
    col, speed, log = core.Collector(), core.Speed(), []
    batch = advance_at = next_frame = None
    seen = 0
    for e in core.stream(speed=10):
        before, m = col.m, col.add(e)
        if batch is None:
            batch, next_batch = (m, Counter()), m + BATCH_EVERY  # nothing batched yet
        if before is not None and m > before:  # a minute ended and its file is closed
            if advance_at and m >= advance_at:
                speed.advance(batch[0])
                log.append(f"{core.hhmm(m)}  speed layer advanced to {core.hhmm(batch[0])}")
                advance_at = None
            if m >= next_batch:
                batch, next_batch, advance_at = core.batch_view(m - BATCH_LAG), m + BATCH_EVERY, m + 1
                log.append(f"{core.hhmm(m)}  batch view published, horizon {core.hhmm(batch[0])}")
        if core.is_edit(e):
            speed.add(e, m)
            seen += 1
        t = core.arrival(e)
        if next_frame is None or t >= next_frame:
            frame(t, batch, speed, seen, log)
            next_frame = t + REFRESH
    col.close()
    frame(t, batch, speed, seen, log)


def frame(t, batch, speed, seen, log):
    T, view = batch
    total = core.query(batch, speed)
    held = sorted(speed.buckets)
    span = f"{core.hhmm(held[0])}-{core.hhmm(held[-1])}" if held else "none yet"
    lines = [f"{core.clock(t)}  edits seen {seen}, query total {sum(total.values())}",
             f"batch view: arrivals before {core.hhmm(T)}   speed layer: minutes {span}", *log[-2:], "",
             f"{'page':60} {'batch':>6} {'speed':>6} {'total':>6}"]
    for p, c in total.most_common(TOP):
        lines.append(f"{p[:60]:60} {view[p]:6} {c - view[p]:6} {c:6}")
    core.show(lines)


if __name__ == "__main__":
    core.run(main)
