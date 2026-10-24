"""Build the judging worksheet for the own gold set: a pool of candidate documents for every query.

    uv run python scripts/build_candidates.py

For each query in eval/own/queries.tsv the pool is the union of:
- the top 10 of bm25, dense and hybrid (no Claude calls);
- up to 20 documents that match the query's pattern in judging/keywords.tsv (a keyword search,
  case-insensitive, most matches first), so the pool is not only what the systems returned.
Each query's candidates are shuffled with a fixed seed and the worksheet does not say where a
candidate came from, so the judgment cannot lean toward one system.

It writes judging/candidates.tsv: qid, query, docid, title, words, snippet, rel. The snippet is the
first sentence that matches the keyword pattern, or else the document's first sentence; it is a hint
for finding the place to read, not a reason to judge. Fill rel with 1 (relevant) or 0 (not), after
reading the document in corpora/own/docs/<docid>.md. scripts/worksheet_to_qrels.py turns the 1s into
eval/own/qrels.txt.
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

from p2 import config, corpus as corpus_mod, paths
from p2.retrievers import build
from p2.runfile import read_queries

ROOT = Path(__file__).resolve().parents[1]
SYSTEMS = ("bm25", "dense", "hybrid")
TOP = 10
KEYWORD_CAP = 20


def sentences(text: str) -> list[str]:
    lines = text.splitlines()
    title = lines[0][2:].strip() if lines and lines[0].startswith("# ") else ""
    body = "\n".join(l for l in lines[1:] if l.strip() and not l.startswith("#") and l.strip() != title)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", body) if s.strip()]


def snippet(text: str, pattern: re.Pattern | None) -> str:
    sents = sentences(text)
    if pattern:
        for s in sents:
            if pattern.search(s):
                return s[:300]
    return (sents[0] if sents else "")[:300]


def main() -> None:
    cfg = config.load(ROOT)
    corpus = corpus_mod.load(cfg.root, "own")
    queries, problems = read_queries(paths.queries(cfg.root, "own", "own"), require_origin=True)
    if problems:
        sys.exit("\n".join(problems))
    patterns = {}
    kw_file = ROOT / "judging" / "keywords.tsv"
    for line in kw_file.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            qid, regex = line.split("\t", 1)
            patterns[qid] = re.compile(regex, re.I)
    systems = {name: build(name, corpus, cfg) for name in SYSTEMS}
    rows = ["qid\tquery\tdocid\ttitle\twords\tsnippet\trel"]
    sizes = []
    for q in queries:
        pool: set[str] = set()
        for system in systems.values():
            pool.update(d for d, _ in system.search(q.text, TOP))
        pattern = patterns.get(q.qid)
        if pattern:
            hits = sorted(((len(pattern.findall(doc.text)), docid) for docid, doc in corpus.docs.items() if pattern.search(doc.text)), key=lambda h: (-h[0], h[1]))
            pool.update(docid for _, docid in hits[:KEYWORD_CAP])
        order = sorted(pool)
        random.Random(q.qid).shuffle(order)
        sizes.append((q.qid, len(order)))
        for docid in order:
            doc = corpus.docs[docid]
            snip = snippet(doc.text, pattern).replace("\t", " ").replace("\n", " ")
            rows.append(f"{q.qid}\t{q.text}\t{docid}\t{doc.title}\t{len(doc.text.split())}\t{snip}\t")
    out = ROOT / "judging" / "candidates.tsv"
    out.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {out.relative_to(ROOT)}: {len(rows) - 1} candidates for {len(queries)} queries")
    print("  " + ", ".join(f"{qid} {n}" for qid, n in sizes))


if __name__ == "__main__":
    main()
