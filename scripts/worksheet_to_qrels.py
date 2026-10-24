"""Turn the judged worksheet into eval/own/qrels.txt.

    uv run python scripts/worksheet_to_qrels.py

Reads judging/candidates.tsv (after you filled the rel column) and writes one line `qid 0 docid 1`
for every row marked 1, keeping the comment lines at the top of eval/own/qrels.txt.
Rows marked 0 are judged not relevant and rows left blank are not judged; both write nothing,
but the counts are printed so you can see what is left. A query with no 1 is listed, because
p2 check needs at least one relevant document per query.
It accepts a file saved by Excel or another editor (a byte order mark, Windows line endings).
It also takes extra relevant documents you found by reading, from judging/extra.tsv
(qid<TAB>docid, one per line) when that file exists.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    sheet = ROOT / "judging" / "candidates.tsv"
    lines = sheet.read_text(encoding="utf-8-sig").splitlines()
    head = lines[0].split("\t")
    i_q, i_d, i_r = head.index("qid"), head.index("docid"), head.index("rel")
    docs = {p.stem for p in (ROOT / "corpora" / "own" / "docs").glob("*.md")}
    relevant: dict[str, set[str]] = {}
    counts: Counter = Counter()
    qids: list[str] = []
    for n, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        f = line.rstrip("\r").split("\t")
        qid, docid = f[i_q].strip(), f[i_d].strip()
        rel = f[i_r].strip() if len(f) > i_r else ""
        if qid not in qids:
            qids.append(qid)
        if rel == "1":
            relevant.setdefault(qid, set()).add(docid)
            counts["relevant"] += 1
        elif rel == "0":
            counts["not relevant"] += 1
        elif rel == "":
            counts["not judged"] += 1
        else:
            sys.exit(f"{sheet.name} line {n}: rel is {rel!r}; use 1, 0 or leave it blank")
    extra = ROOT / "judging" / "extra.tsv"
    if extra.exists():
        for line in extra.read_text(encoding="utf-8-sig").splitlines():
            if line.strip() and not line.startswith("#"):
                qid, docid = (x.strip() for x in line.split("\t")[:2])
                if docid not in docs:
                    sys.exit(f"{extra.name}: {docid!r} is not a document in corpora/own/docs/")
                relevant.setdefault(qid, set()).add(docid)
                counts["extra relevant"] += 1
    qrels = ROOT / "eval" / "own" / "qrels.txt"
    comments = [l for l in qrels.read_text(encoding="utf-8").splitlines() if l.startswith("#")]
    out = [f"{qid} 0 {docid} 1" for qid in qids + sorted(set(relevant) - set(qids)) for docid in sorted(relevant.get(qid, ()))]
    qrels.write_text("\n".join(comments + out) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {len(out)} judgments to eval/own/qrels.txt ({', '.join(f'{v} {k}' for k, v in counts.items())}).")
    empty = [q for q in qids if q not in relevant]
    if empty:
        print(f"No relevant document yet for: {', '.join(empty)}")


if __name__ == "__main__":
    main()
