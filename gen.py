"""Generate the page-view master dataset: one immutable JSONL file per arrival hour."""
import json
import random
import sys
from pathlib import Path

DAY = "2026-10-26"
HOURS = range(8, 16)  # arrival hours 08:00-15:59
PER_HOUR = 20_000
LATE = 0.03  # share of events that arrive up to 90 min after they happened
MASTER = Path(__file__).parent / "data" / "master"


def catalogue(rng):
    urls = ["/home", "/news/8812"]
    while len(urls) < 400:
        section = rng.choice(["news", "sport", "tech", "culture"])
        u = f"/{section}/{rng.randrange(1000, 9999)}"
        if u not in urls:
            urls.append(u)
    visitors = sorted({f"{rng.getrandbits(24):06x}" for _ in range(30_000)})
    rng.shuffle(visitors)
    return urls, visitors + [f"bot-{i:02}" for i in range(5)]


def cumulative(weights):
    out, s = [], 0.0
    for w in weights:
        s += w
        out.append(s)
    return out


def generate():
    rng = random.Random(2026)
    urls, visitors = catalogue(rng)
    url_w = cumulative(1 / (i + 1) ** 1.1 for i in range(len(urls)))
    humans = len(visitors) - 5
    vis_w = cumulative([1 / (i + 1) ** 0.6 for i in range(humans)] + [3.5] * 5)
    refs, ref_w = ["google", "direct", "facebook", "newsletter", "twitter"], [45, 25, 15, 10, 5]
    MASTER.mkdir(parents=True, exist_ok=True)
    eid = 0
    for h in HOURS:
        start, lines = h * 3600, []
        offsets = sorted(rng.uniform(0, 3600) for _ in range(PER_HOUR))
        for arr in offsets:
            t = start + arr
            if rng.random() < LATE:
                t = start - rng.uniform(60, 5400)
            t = int(t)
            eid += 1
            ts = f"{DAY}T{t // 3600:02}:{t // 60 % 60:02}:{t % 60:02}"
            e = {"id": eid, "ts": ts,
                 "url": rng.choices(urls, cum_weights=url_w)[0],
                 "visitor": rng.choices(visitors, cum_weights=vis_w)[0],
                 "ref": rng.choices(refs, ref_w)[0]}
            lines.append(json.dumps(e) + "\n")
        # Never rewrite an existing file: the master is append-only.
        path = MASTER / f"arrival={DAY}T{h:02}.jsonl"
        if not path.exists():
            path.write_text("".join(lines))
            print(f"wrote {path.name}", file=sys.stderr)


if __name__ == "__main__":
    generate()
