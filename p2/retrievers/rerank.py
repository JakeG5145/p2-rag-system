"""Reranking: Claude reorders 20 candidates from bm25 and dense, one listwise claude -p call per query.

It is rerank_one() from the 13 lab's pipeline.py, with four changes:
- the candidates are not hybrid's top 20 but bm25's and dense's own rankings interleaved (bm25 1st,
  dense 1st, bm25 2nd, ...), skipping repeats, until there are 20: about each system's top 10.
  On the practice queries this pool held 0.833 of the relevant sections against 0.725 for hybrid's
  top 20, because RRF k = 60 can push a section one system ranks 3rd below 20th (p03, 75.1714);
- each candidate is shown as its document's title and its best-matching chunk (the first chunk of
  that document in hybrid's chunk ranking, up to [chunking] words), not the first 600 characters,
  so a long section shows Claude the part that matched;
- the schema's items are bounded to 1..20, so a number that names no passage cannot come back;
- the prompt names no corpus, so the same reranker runs on the shared corpus and on your own.

A failed call, or a reply that is not each number once, keeps the interleaved order for that query
(with a warning). The documents below the 20 follow in hybrid's order. A document's score is
1 / its new rank, so the run file's scores fall with rank.
search_chunks builds the same kind of pool from bm25's and dense's chunk rankings, for `p2 answer`.
"""

from __future__ import annotations

import sys

from p2 import claude
from p2.corpus import docid_of
from p2.retrievers import build as build_system

NEEDS_CLAUDE = True
CANDIDATES = 20

PROMPT = """Below are {n} passages from a document collection, numbered 1 to {n}, and a search query.
Each passage starts with the title of the document it comes from.
Order the passages from the most useful for answering the query to the least useful.
Reply with all {n} passage numbers, each exactly once, best first.

Query: {query}

{passages}"""


def schema(n: int) -> dict:
    return {
        "type": "object",
        "properties": {
            "order": {
                "type": "array",
                "items": {"type": "integer", "minimum": 1, "maximum": n},
                "minItems": n,
                "maxItems": n,
            }
        },
        "required": ["order"],
    }


def interleave(first: list[str], second: list[str], n: int) -> list[str]:
    """first[0], second[0], first[1], second[1], ... skipping repeats, until n ids (or both run out)."""
    out: list[str] = []
    seen: set[str] = set()
    for i in range(max(len(first), len(second))):
        for ranking in (first, second):
            if i < len(ranking) and ranking[i] not in seen:
                seen.add(ranking[i])
                out.append(ranking[i])
                if len(out) == n:
                    return out
    return out


class Rerank:
    candidates = CANDIDATES  # how many candidates Claude reorders; a variant such as rerank_c10 changes only this

    def __init__(self, corpus, cfg):
        self.corpus = corpus
        self.cfg = cfg
        self.model = cfg.model
        self.hybrid = build_system("hybrid", corpus, cfg)
        self.bm25, self.dense = self.hybrid.bm25, self.hybrid.dense
        self.chunk_text = {c.id: c.text for c in self.dense.chunks}
        self.n_docs = len(corpus.docs)
        self.n_chunks = len(self.chunk_text)

    def passage(self, chunk_id: str) -> str:
        doc = self.corpus.docs[docid_of(chunk_id)]
        text = self.chunk_text[chunk_id]
        if text.startswith("# "):
            text = text.split("\n", 1)[1] if "\n" in text else ""
        return f"{doc.title}\n{text.strip()}"

    def reorder(self, query: str, chunk_ids: list[str]) -> list[int]:
        """The candidates' indexes in Claude's order, or their pool order if the call or reply is unusable."""
        n = len(chunk_ids)
        keep = list(range(n))
        if n < 2:
            return keep
        passages = "\n\n".join(f"[{i}] {self.passage(c)}" for i, c in enumerate(chunk_ids, 1))
        try:
            reply = claude.call(PROMPT.format(n=n, query=query, passages=passages), schema(n), model=self.cfg.model, cache_dir=claude.cache_folder(self.cfg))
        except Exception as e:  # ClaudeBlocked is a BaseException, so p2 check still sees it
            print(f"WARNING: the rerank call failed ({e}); kept the candidate order", file=sys.stderr)
            return keep
        if reply.error:
            print(f"WARNING: the rerank call failed ({reply.error}); kept the candidate order", file=sys.stderr)
            return keep
        order = (reply.output or {}).get("order")
        if not isinstance(order, list) or sorted(order) != list(range(1, n + 1)):
            print(f"WARNING: the reply was not each of 1 to {n} once ({order}); kept the candidate order", file=sys.stderr)
            return keep
        return [i - 1 for i in order]

    @staticmethod
    def scored(ids: list[str], k: int) -> list[tuple[str, float]]:
        return [(i, 1 / rank) for rank, i in enumerate(ids[:k], 1)]

    def search(self, text: str, k: int) -> list[tuple[str, float]]:
        keyword = [d for d, s in self.bm25.search(text, self.n_docs) if s > 0]
        semantic = [d for d, _ in self.dense.search(text, self.n_docs)]
        pool = interleave(keyword, semantic, self.candidates)
        wanted, best_chunk = set(pool), {}
        for chunk_id, _ in self.hybrid.search_chunks(text, self.n_chunks):
            docid = docid_of(chunk_id)
            if docid in wanted and docid not in best_chunk:
                best_chunk[docid] = chunk_id
                if len(best_chunk) == len(wanted):
                    break
        order = self.reorder(text, [best_chunk[d] for d in pool])
        rest = [d for d, _ in self.hybrid.search(text, self.n_docs) if d not in wanted]
        return self.scored([pool[i] for i in order] + rest, k)

    def search_chunks(self, text: str, k: int) -> list[tuple[str, float]]:
        keyword = [c for c, s in self.bm25.search_chunks(text, self.n_chunks) if s > 0]
        semantic = [c for c, _ in self.dense.search_chunks(text, self.n_chunks)]
        pool = interleave(keyword, semantic, self.candidates)
        order = self.reorder(text, pool)
        wanted = set(pool)
        rest = [c for c, _ in self.hybrid.search_chunks(text, max(k, self.candidates) + self.candidates) if c not in wanted]
        return self.scored([pool[i] for i in order] + rest, k)


def build(corpus, cfg):
    return Rerank(corpus, cfg)
