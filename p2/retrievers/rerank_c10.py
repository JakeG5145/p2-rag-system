"""The reranker over 10 candidates instead of 20 (stretch option 3, cost and latency).

Everything else is rerank.py: the same pool (bm25 and dense interleaved, so about each one's top 5),
the same passages, prompt and model. Half the passages should mean about half the input tokens per
call; the stretch-cost table weighs that saving against what it costs in MRR@10.
Run on the shared practice queries only.
"""

from __future__ import annotations

from p2.retrievers.rerank import Rerank

NEEDS_CLAUDE = True
BASE = "rerank"


class Rerank10(Rerank):
    candidates = 10


def build(corpus, cfg):
    return Rerank10(corpus, cfg)
