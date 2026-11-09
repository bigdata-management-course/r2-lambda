"""Instructor tool: python3 record.py records MINUTES of the live stream into recording.jsonl.gz."""
import gzip
import json
import time

import core

MINUTES = 20


def slim(e):
    m = e["meta"]
    meta = {k: m[k] for k in ("dt", "topic", "partition", "offset")}
    keep = ("timestamp", "bot", "wiki", "server_name", "namespace", "title", "type")
    return dict({k: e.get(k) for k in keep}, meta=meta)


if __name__ == "__main__":
    tmp = core.RECORDING.with_suffix(".part")
    end, n = time.time() + 60 * MINUTES, 0
    with gzip.open(tmp, "wt", encoding="utf-8") as f:
        for e in core.live():
            f.write(json.dumps(slim(e), ensure_ascii=False, separators=(",", ":")) + "\n")
            n += 1
            if n % 5000 == 0:
                print(f"{n} events", flush=True)
            if time.time() > end:
                break
    tmp.replace(core.RECORDING)
    print(f"{n} events -> {core.RECORDING.name}")
