"""What you observed. Replace each None with the value the program showed you, then run check.py.

Write numbers as numbers (1803, not "1803"), pages as printed ("enwiki:Main Page"), and a percentage
as the number printed before the % sign (12.5). Undo every edit before the next item.
"""

# === IN CLASS ===================================================================================

# 1. The naive counter: python3 counter.py, as it is (version 2 runs in minutes 6-8)
V2_ROW = None            # final count of the broken row enwiki:
FIRST_REAL_COUNT = None  # final count of the first real page (not a broken "wiki:" row) in the list

# 2. Batch from raw facts: python3 collect.py, then python3 batch.py
BATCH_PAGES = None       # "pages" in the batch view
V2_PAGES = None          # "pages" in the view with KEY = core.page_v2 in batch.py

# 3. Event time vs arrival time: python3 batch.py
LATE_EVENTS = None       # late edits (more than LATE = 10 s)
MOVED = None             # edits that sit in the file of a later minute than the one they happened in

# 4. The seam: in core.py query(), delete since=T, then python3 dashboard.py
SEAM_SEEN = None         # "edits seen" in the frame 23:02:19
SEAM_TOTAL = None        # "query total" in the same frame

# 5. Kappa: python3 kappa.py with KEEP = lambda e: not e["bot"]
BOT_SHARE = None         # dropped, in % as printed
ENWIKI_KEPT = None       # the "kept" column of enwiki

# === AT HOME: the same tools, new questions =====================================================

OFFSET_1000 = None       # 1. tap.py with SHOW = 1000: Kafka offset of event 1000
LEON_NO_BUG = None       # 2. counter.py with V2 = None: final count of frwiki:Léon Grandin
LATE_20 = None           # 3. batch.py with LATE = 20: late edits
BATCH_LAG4 = None        # 4. dashboard.py with BATCH_LAG = 4: batch column of the top page, last frame
NEW_KEPT = None          # 5. kappa.py with KEEP = lambda e: e["type"] == "new" (new articles only): kept
NEW_ENWIKI = None        #    and the "kept" column of enwiki
