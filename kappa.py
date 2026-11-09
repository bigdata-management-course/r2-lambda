"""Act 4, Kappa: python3 kappa.py [--speed N] [--live]. One stream job; reprocessing = replaying the log."""
from collections import Counter

import core

KEEP = lambda e: True  # the editors' request, humans only: lambda e: not e["bot"]
TOP = 8


def main():
    edits, bots, kept, now = Counter(), Counter(), Counter(), None
    for e in filter(core.is_edit, core.stream(speed=0)):  # the log is stored: replay it as fast as we can
        m = core.minute(core.arrival(e))
        if now is not None and m > now:
            frame(edits, bots, kept, now, e)
        now = max(m, now or m)
        edits[e["wiki"]] += 1
        bots[e["wiki"]] += e["bot"]
        kept[e["wiki"]] += bool(KEEP(e))
    frame(edits, bots, kept, now, e)


def frame(edits, bots, kept, now, e):
    n, k = sum(edits.values()), sum(kept.values())
    head = f"{n} edits replayed, {k} kept, {n - k} dropped ({(n - k) / n:.1%})"
    lines = [f"{core.hhmm(now)}  offset {e['meta']['offset']}  {head}",
             f"  {'wiki':14} {'edits':>6} {'by bots':>8} {'bot share':>10} {'kept':>6}"]
    for w, c in edits.most_common(TOP):
        lines.append(f"  {w:14} {c:6} {bots[w]:8} {bots[w] / c:10.1%} {kept[w]:6}")
    core.show(lines)


if __name__ == "__main__":
    core.run(main)
