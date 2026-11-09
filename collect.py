"""Act 2, the collector: python3 collect.py [--speed N] [--live] appends raw events to data/master/."""
import core


def main():
    col, n = core.Collector(), 0
    for e in core.stream(speed=30):
        before = col.m
        if col.add(e) != before and before is not None:
            print(f"closed {core.fname(before)}  {n} events")
            n = 0
        n += 1
    col.close()
    print(f"closed {core.fname(col.m)}  {n} events  (end of the recording)")


if __name__ == "__main__":
    core.run(main)
