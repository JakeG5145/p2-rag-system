"""Fetch the Wikipedia dog breed articles for the own corpus, as plain text, into a folder outside the repo.

    uv run --no-project python scripts/fetch_dog_breeds.py ../p2-raw/dog-breeds

Which articles: every article linked from "List of dog breeds" that sits in a category named
"Dog breeds originating in ..." (that drops links such as "Kennel club" or a country).
What each file holds: "# <title>", a blank line, and the article's plain-text extract from the
MediaWiki API, with section headings as "## ..." and the trailing See also / Notes / References /
Further reading / External links sections left out.
Next to the files it writes sources.tsv: file stem, title, the permanent link to the revision
fetched, and that revision id, which is what the manifest's source column records.

Wikipedia text is CC BY-SA 4.0. The API asks scripts to identify themselves and go slowly, so this
sends a User-Agent naming the project, waits between requests, and backs off on HTTP 429.
"""

from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://en.wikipedia.org/w/api.php"
UA = "p2-rag-system/0.1 (course project; https://github.com/JakeG5145/p2-rag-system)"
LIST_PAGE = "List of dog breeds"
BREED_CATEGORY = re.compile(r"^Category:Dog breeds originating in ")
DROP_SECTIONS = {"see also", "notes", "references", "further reading", "external links", "bibliography",
                 "sources", "citations", "footnotes", "notes and references", "literature", "works cited"}
PAUSE_S = 1.0


def api(**params) -> dict:
    params.update(format="json", formatversion="2", maxlag="5")
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(8):
        time.sleep(PAUSE_S)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                data = json.load(r)
            if data.get("error", {}).get("code") == "maxlag":
                time.sleep(5 * (attempt + 1))
                continue
            return data
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504):
                raise
            wait = int(e.headers.get("Retry-After") or 0) or 10 * 2 ** attempt
            print(f"  HTTP {e.code}, waiting {wait} s", file=sys.stderr, flush=True)
            time.sleep(wait)
    raise RuntimeError(f"gave up on {url}")


def list_links() -> list[str]:
    links, cont = [], {}
    while True:
        r = api(action="query", prop="links", titles=LIST_PAGE, pllimit="max", plnamespace=0, **cont)
        links += [l["title"] for l in r["query"]["pages"][0].get("links", [])]
        if "continue" not in r:
            return links
        cont = r["continue"]


def breed_titles(candidates: list[str]) -> list[str]:
    """The candidates (after redirects) that are in a 'Dog breeds originating in' category."""
    keep: set[str] = set()
    for i in range(0, len(candidates), 50):
        batch, cont = candidates[i : i + 50], {}
        while True:
            r = api(action="query", prop="categories", titles="|".join(batch), redirects=1, cllimit="max", **cont)
            for page in r["query"]["pages"]:
                if any(BREED_CATEGORY.match(c["title"]) for c in page.get("categories", [])):
                    keep.add(page["title"])
            if "continue" not in r:
                break
            cont = r["continue"]
        print(f"  checked {min(i + 50, len(candidates))} of {len(candidates)} links, {len(keep)} breeds so far", file=sys.stderr, flush=True)
    return sorted(keep)


def stem_for(title: str) -> str:
    """A clean file stem: 'Boxer (dog)' -> 'boxer-dog'."""
    s = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def to_markdown(title: str, extract: str) -> str:
    """'== History ==' headings become '## History'; the trailing reference-type sections go."""
    out, dropping = [], False
    for line in extract.splitlines():
        m = re.match(r"^(={2,6})\s*(.*?)\s*\1\s*$", line)
        if m:
            level = len(m.group(1))
            if level == 2:
                dropping = m.group(2).strip().lower() in DROP_SECTIONS
            if not dropping:
                out.append("#" * level + " " + m.group(2))
            continue
        if not dropping:
            out.append(line.rstrip())
    body = re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()
    body = re.sub(r"(?m)^(#{2,6} .*)\n+(?=#{2,6} |\Z)", "", body)  # headings left with nothing under them
    return f"# {title}\n\n{body.strip()}\n"


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    print(f"Reading the links of '{LIST_PAGE}'", file=sys.stderr)
    titles = breed_titles(list_links())
    print(f"{len(titles)} breed articles; fetching their text", file=sys.stderr, flush=True)
    sources = out / "sources.tsv"
    done = {}
    if sources.exists():
        for line in sources.read_text(encoding="utf-8").splitlines()[1:]:
            stem, title, *_ = line.split("\t")
            done[title] = line
    stems: dict[str, str] = {}
    rows = []
    for n, title in enumerate(titles, 1):
        stem = stem_for(title)
        if stem in stems:
            print(f"  skipped {title!r}: its file name {stem} is taken by {stems[stem]!r}", file=sys.stderr)
            continue
        stems[stem] = title
        if title in done and (out / f"{stem}.md").exists():
            rows.append(done[title])
            continue
        r = api(action="query", prop="extracts|revisions", explaintext=1, exsectionformat="wiki", rvprop="ids", titles=title, redirects=1)
        page = r["query"]["pages"][0]
        text = page.get("extract") or ""
        if not text.strip():
            print(f"  skipped {title!r}: empty extract", file=sys.stderr)
            continue
        revid = page["revisions"][0]["revid"]
        (out / f"{stem}.md").write_text(to_markdown(page["title"], text), encoding="utf-8", newline="\n")
        link = f"https://en.wikipedia.org/w/index.php?title={urllib.parse.quote(page['title'].replace(' ', '_'))}&oldid={revid}"
        rows.append(f"{stem}\t{page['title']}\t{link}\t{revid}")
        if n % 25 == 0:
            print(f"  fetched {n} of {len(titles)}", file=sys.stderr, flush=True)
            sources.write_text("stem\ttitle\tsource\trevid\n" + "\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    sources.write_text("stem\ttitle\tsource\trevid\n" + "\n".join(rows) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {len(rows)} articles and sources.tsv to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
