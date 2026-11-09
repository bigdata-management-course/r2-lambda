# Recitation 2: a live Wikipedia dashboard, Lambda and Kappa

The code of Recitation 2 (Lecture 2: Lambda and Kappa architectures). One question, asked of the live
stream of every change on every Wikimedia wiki: *which Wikipedia articles are being edited most right
now, and how much of it is bots?* The counters keep only edits and new pages of Wikipedia articles
(7,211 of the 46,735 recorded events): category and log events are bookkeeping, and Wikidata items,
Commons files, talk and user pages are not articles. Five acts, one small program each; every act ends
with an incident that forces the next architectural move. In class you run each act and record what you
see in `observations.py`; at home you answer new questions with the same tools. Not graded.

## Setup

You need Python 3.8+ and git. No packages, no GitHub account: the repository is public.

```sh
git clone https://github.com/bigdata-management-course/r2-lambda.git
cd r2-lambda
python3 check.py
```

The last two lines must be:

```
in class: c1 FAIL  c2 FAIL  c3 FAIL  c4 FAIL  c5 FAIL
at home:  h1 FAIL  h2 FAIL  h3 FAIL  h4 FAIL  h5 FAIL
```

`FAIL` only means "not filled in yet". On Windows use `py` or `python` instead of `python3`.

## The acts

Every program replays the recording `recording.jsonl.gz` at the speed of its own default; `--speed N`
replays N times faster than real time (`--speed 1` is real time, `--speed 0` as fast as possible).
`--live` reads the real stream instead (the instructor does this on the projector; please don't all
connect at once from the campus network). Ctrl-C stops any of them.

| Act | Command | What it is |
|---|---|---|
| 0 | `python3 tap.py` | The firehose, then one event close up: event time, arrival time, bot flag, Kafka offset. |
| 1 | `python3 counter.py` | The naive dashboard: one counter per page. Version 2, with a bug, runs for 3 minutes. |
| 2 | `python3 collect.py`, then `python3 batch.py` | Raw events into `data/master/`, one file per arrival minute; the batch view recomputed from them. |
| 3 | `python3 dashboard.py` | Lambda: batch view + speed layer, merged by the query, refreshed live. |
| 4 | `python3 kappa.py` | Kappa: one stream job; reprocessing = replaying the log. Edits and bot share per wiki. |

The settings you change are the CAPITALISED names at the top of each file. `core.py` holds the
architecture (stream, master dataset, batch view, speed layer, query); `observations.py` says, for
each item, what to change and what to run. Undo every change afterwards (`git checkout <file>`):
`check.py` warns if `core.py` or the recording differs from the original. `data/` is rebuilt by the
programs; delete it to start over.

## Checking your observations

Write the value you saw into `observations.py`, then run `python3 check.py c3` (or `h1 h2`, or nothing
for all). The checker compares digests and never shows the expected value. Your answers stay in your
own copy; there is nothing to push or submit.

## Where the data comes from

[Wikimedia EventStreams](https://wikitech.wikimedia.org/wiki/Event_Platform/EventStreams_HTTP_Service),
stream `recentchange`: every edit, page creation, log entry and category change on the Wikimedia wikis,
served over HTTP as Server-Sent Events from Wikimedia's Kafka. `recording.jsonl.gz` holds 20 minutes of
it (46,735 events, 2026-11-07 22:52:19-23:12:18 UTC), recorded with `record.py`, keeping only the fields
the code reads (`wiki`, `server_name`, `namespace`, `title`, `type`, `bot`, `timestamp`, and from `meta`
the arrival time `dt` and the Kafka `topic`, `partition`, `offset`).

The EventStreams documentation gives no data license of its own; it asks clients to send a
descriptive `User-Agent` (see [API:Etiquette](https://www.mediawiki.org/wiki/API:Etiquette)), which
`core.py` does, and notes that the server closes every connection after 15 minutes (the reader resumes
with `Last-Event-ID`). The service's API description points to the
[Wikimedia Foundation Terms of Use](https://wikimediafoundation.org/wiki/Terms_of_Use). Page titles
belong to the wikis they come from.
