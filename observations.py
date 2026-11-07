"""What you observed. Replace each None with the value the demo showed you, then run check.py.

Write numbers as numbers (1803, not "1803") and hours or timestamps as strings ("2026-10-26T09:15:00").
worksheet.pdf says, for each one, which demo to run and what to change.
"""

# === "Your turn", one per Lecture 2 concept: 6-7 in class, 1-5 at home =======

# 1. Immutable master dataset: append arrival hour 16 with gen.py
NEW_FIRST_ID = None         # "id" of the first fact in the new file arrival=2026-10-26T16.jsonl

# 2. Event time vs arrival time: demo.py step 2 with ARRIVAL = H[8]
LATE_IN_08 = None           # late facts in the file arrival=2026-10-26T08
EARLIEST_IN_08 = None       # earliest event time in that file

# 3. Batch view: demo.py step 3 with KEY grouping by (ref, event hour)
REF_ROWS = None             # rows of the view with HORIZON = H[12]
GOOGLE_10 = None            # views of ('google', '2026-10-26T10') in that view

# 4. Serving layer: demo.py step 4 with ASK = ("/home", H[13])
HOME_13_BEFORE = None       # get() before the swap
HOME_13_AFTER = None        # get() after the swap

# 5. Speed layer: demo.py step 5 with STREAM = lam.deliver
DUPLICATES = None           # views counted minus 40000
NEWS_12_WITH_DUPS = None    # realtime of /news/8812 12:00

# 6. Query = batch + speed: demo.py step 6 with since=T removed in lam.query
DOUBLE_11 = None            # total at 11:00 in the middle table

# 7. Kappa: demo.py step 7 with KEEP dropping bot visitors
BOT_VIEWS = None            # views dropped by KEEP

# === AT HOME: the same tools, new questions ===================================

STORE_NEWS_12 = None        # 1. demo.py step 8: the mutable store's ('/news', 12:00) counter
MOST_LATE_FILE = None       # 2. arrival hour whose file has the most late facts
GOOGLE_SHARE_11 = None      # 3. google's share of all 11:00 views, all facts, round(x, 3)
KEYS_AFTER_SWAP = None      # 4. keys of the view published with horizon H[14]
LATE_11_IN_BUCKET_13 = None  # 5. /news/8812 11:00 views held in speed bucket 13
LOST_BY_SPLIT = None        # 6. {event hour: views} an event-hour split drops, all URLs
V2_NEWS_11 = None           # 7. /news/8812 11:00 in the bot-free Kappa view
