"""Act 1, the naive dashboard: python3 counter.py [--speed N] [--live] keeps one counter per page."""
import sys
from collections import Counter

import core

TOP = 10
V2 = (6, 9)  # minutes of the run in which the buggy version 2 is deployed; None = never
TRACK = "frwiki:Léon Grandin"  # edited 1, 4, 3 times in the v2 minutes: watch its history stall


def main():
    n, last, history, start, now = Counter(), Counter(), [], None, None
    for e in filter(core.is_edit, core.stream(speed=30)):
        m = core.minute(core.arrival(e))
        start = m if start is None else start
        if now is not None and m > now:
            frame(n, last, history, now, start)
            last = Counter(n)
        now = max(m, now or m)
        n[core.page_v2(e) if v2(now - start) else core.page(e)] += 1
    frame(n, last, history, now, start)


def v2(minute):
    return V2 and V2[0] <= minute < V2[1]


def frame(n, last, history, now, start):
    history.append(n[TRACK] - last[TRACK])
    version = "version 1"
    if v2(now - start):
        version = f"VERSION 2  deployed {core.hhmm(start + V2[0])}"
        if sys.stdout.isatty():
            version = f"\033[1;7;31m {version} \033[0m"
    elif V2 and now - start >= V2[1]:
        version += f"  (v2 rolled back at {core.hhmm(start + V2[1])})"
    lines = [f"{core.hhmm(now)}  minute {now - start}  {version}  {sum(n.values())} edits",
             f"  {'count':>6}  {'+min':>5}  page"]
    lines += [f"  {c:6}  {'+' + str(c - last[p]):>5}  {p[:70]}" for p, c in n.most_common(TOP)]
    if V2 and now - start >= V2[1]:
        stuck = sum(c for p, c in n.items() if p.endswith(":"))
        lines.append(f'{stuck} edits stuck under "wiki:" keys: the counter kept sums, not events')
    lines.append(f"{TRACK} per minute: {' '.join(map(str, history))}")
    core.show(lines)


if __name__ == "__main__":
    core.run(main)
