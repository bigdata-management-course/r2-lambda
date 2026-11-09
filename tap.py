"""Act 0, the tap: python3 tap.py [--speed N] [--live] prints the firehose, then one event in detail."""
import core

SHOW = 20  # events to print before the close-up


def main():
    for i, e in enumerate(core.stream(speed=1), 1):
        who = "bot  " if e["bot"] else "human"
        print(f"{core.clock(core.arrival(e))}  {who}  {e['type']:10}  {core.page(e)[:70]}")
        if i == SHOW:
            break
    lag = core.arrival(e) - e["timestamp"]
    m = e["meta"]
    print(f"\nevent {i}, close up:")
    print(f"  wiki, title   {e['wiki']}, {e['title']}")
    print(f"  type, bot     {e['type']}, {e['bot']}")
    print(f"  timestamp     {e['timestamp']} = {core.clock(e['timestamp'])}   event time: the edit happened")
    print(f"  meta.dt       {m['dt']}   arrival time: Kafka got it, {lag:.1f} s later")
    print(f"  meta.topic    {m['topic']}, partition {m['partition']}, offset {m['offset']}")
    print("\nActs 1-4 count only edits and new pages of Wikipedia articles (namespace 0): categorize and log"
          " events are bookkeeping, and Wikidata items, Commons files, talk and user pages are not articles.")


if __name__ == "__main__":
    core.run(main)
