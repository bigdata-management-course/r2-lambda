"""Going further (optional, at home): replace each NotImplementedError, then run check.py g1 g2."""
import hashlib

import lam


def h64(s):
    return int.from_bytes(hashlib.blake2b(s.encode(), digest_size=8).digest(), "big")


# --- g1: an idempotent speed layer under at-least-once delivery (concept 5) ---
class DedupSpeed(lam.Speed):
    """Counts each event id once; memory for ids is released by advance()."""

    def __init__(self, horizon):
        super().__init__(horizon)
        self.seen = {}  # arrival hour -> set of event ids already counted

    def on_event(self, arrival, e):
        raise NotImplementedError

    def advance(self, horizon):
        raise NotImplementedError


# --- g2: HyperLogLog, unique visitors that can be merged (concepts 3 and 6) ---
class HLL:
    def __init__(self, p=10):
        self.p, self.m = p, 1 << p
        self.reg = bytearray(self.m)

    def add(self, item):
        raise NotImplementedError

    def merge(self, other):
        """A new HLL that estimates |A u B|."""
        raise NotImplementedError

    def count(self):
        raise NotImplementedError
