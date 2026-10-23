"""Dense retrieval: embed every chunk once, embed the query, and rank chunks by cosine similarity.

It is the embedding arm of the 12 lab's retrieve.py (dense_rankings), moved from whole articles to
chunks: the chunk vectors come from p2.embed.doc_vectors, which caches them in .cache/vectors/, and
one matrix product against the query vector scores every chunk. ChunkScorer lifts those scores to
documents (a document scores its best chunk).

The model is bge-small-en-v1.5 (fastembed), a small contextual model, chosen for the paraphrase
queries that bm25 cannot match by shared words. Every vector has length 1, so the dot product is the
cosine similarity. A [dense] table in p2.toml with model = "..." picks another model.
"""

from __future__ import annotations

import numpy as np

from p2 import embed
from p2.retrievers import ChunkScorer

NEEDS_CLAUDE = False


class Dense(ChunkScorer):
    def __init__(self, corpus, cfg):
        super().__init__(corpus, cfg)
        self.model = cfg.table("dense").get("model", embed.BGE)
        self.embedder = embed.load(self.model)
        self.vectors = embed.doc_vectors(self.embedder, [c.text for c in self.chunks], cfg.root)

    def score_chunks(self, text: str) -> np.ndarray:
        if not len(self.chunks):
            return np.zeros(0, dtype=np.float32)
        query = self.embedder.encode([text])[0]
        return self.vectors @ query


def build(corpus, cfg):
    return Dense(corpus, cfg)
