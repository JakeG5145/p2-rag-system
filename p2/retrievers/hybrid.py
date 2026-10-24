"""Hybrid retrieval: reciprocal rank fusion (k = 60) of bm25 and dense.

It is rrf() from the 13 lab's pipeline.py: each document scores the sum of 1 / (60 + rank) over the
rankings it appears in, so only ranks matter and the two systems' score scales never meet.
It fuses full rankings, not top-k lists, because a document 11th in both can belong in the top 10.

One change from the lab: a bm25 result with score 0 shares no word with the query, and its rank is
only padding in document id order, so it is left out of bm25's ranking instead of earning a rank.
search_chunks does the same fusion over chunk rankings, for `p2 answer`.
"""

from __future__ import annotations

from p2.retrievers import build as build_system
from p2.runfile import order

NEEDS_CLAUDE = False
RRF_K = 60


def rrf(rankings, k=RRF_K):
    """Each id scores the sum of 1 / (k + rank) over the rankings it appears in (ranks from 1)."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, 1):
            scores[item] = scores.get(item, 0.0) + 1 / (k + rank)
    return order(scores.items())


class Hybrid:
    rrf_k = RRF_K  # the fusion constant; an ablation such as hybrid_k10 changes only this

    def __init__(self, corpus, cfg):
        self.bm25 = build_system("bm25", corpus, cfg)
        self.dense = build_system("dense", corpus, cfg)
        self.n_docs = len(corpus.docs)
        self.n_chunks = len(self.dense.chunks)

    def _fuse(self, bm25_hits, dense_hits, k):
        keyword = [i for i, s in bm25_hits if s > 0]
        semantic = [i for i, _ in dense_hits]
        return rrf([keyword, semantic], k=self.rrf_k)[:k]

    def search(self, text: str, k: int) -> list[tuple[str, float]]:
        return self._fuse(self.bm25.search(text, self.n_docs), self.dense.search(text, self.n_docs), k)

    def search_chunks(self, text: str, k: int) -> list[tuple[str, float]]:
        return self._fuse(self.bm25.search_chunks(text, self.n_chunks), self.dense.search_chunks(text, self.n_chunks), k)


def build(corpus, cfg):
    return Hybrid(corpus, cfg)
