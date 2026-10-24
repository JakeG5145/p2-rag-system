"""Ablation: hybrid with reciprocal rank fusion at k = 10 instead of 60.

Everything else is hybrid.py: the same bm25 and dense, the same full rankings, the same handling of
bm25's zero scores. With k = 10 a document's share from one ranking is 1 / (10 + rank), so a 1st place
(1/11) counts much more than a 10th (1/20), where k = 60 makes them nearly equal (1/61 against 1/70).
"""

from __future__ import annotations

from p2.retrievers.hybrid import Hybrid

NEEDS_CLAUDE = False
BASE = "hybrid"


class HybridK10(Hybrid):
    rrf_k = 10


def build(corpus, cfg):
    return HybridK10(corpus, cfg)
