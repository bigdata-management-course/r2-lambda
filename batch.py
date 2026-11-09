"""Act 2, the batch layer: python3 batch.py [--live] recomputes the view from all of data/master/."""
from collections import Counter

import core

KEY = core.page  # act 1's bug: core.page_v2
TOP = 10
LATE = 10  # seconds from event time to arrival time that make an edit late


def main():
    files = sorted(core.MASTER.glob("arrival=*.jsonl"))
    _, view = core.batch_view(None, key=KEY)
    print(f"batch view of {len(files)} files, {sum(view.values())} edits, {len(view)} pages")
    for p, c in view.most_common(TOP):
        print(f"  {c:6}  {p[:70]}")

    arrived, happened, late, moved = Counter(), Counter(), [], 0
    for e in filter(core.is_edit, core.facts()):
        a = core.arrival(e)
        arrived[core.minute(a)] += 1
        happened[core.minute(e["timestamp"])] += 1
        moved += core.minute(a) > core.minute(e["timestamp"])
        if a - e["timestamp"] > LATE:
            late.append(e)
    print(f"\n{len(late)} late edits (arrived more than {LATE} s after they happened);"
          f" {moved} edits sit in the file of a later minute than the one they happened in")
    for e in sorted(late, key=lambda e: e["timestamp"] - core.arrival(e))[:3]:
        a = core.arrival(e)
        print(f"  happened {core.clock(e['timestamp'])}, arrived {core.clock(a)}"
              f" (file {core.hhmm(core.minute(a))})  {core.page(e)[:50]}")
    print("\nminute  by arrival  by event time")
    for m in sorted(set(arrived) | set(happened)):
        print(f"  {core.hhmm(m)}  {arrived[m]:10}  {happened[m]:13}")


if __name__ == "__main__":
    core.run(main)
