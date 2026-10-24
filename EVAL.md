# Evaluation report

This is the report on what you built and what the numbers let you claim.
Two kinds of text live here.

The tables between a `p2:begin` comment line and its matching `p2:end` comment line are written by `uv run p2 score` from your committed run files and answers files.
Please do not edit anything between those two lines, because `uv run p2 check` recomputes them and fails when they differ.
A table that says no runs or answers exist yet is waiting for data; run `uv run p2 score` after you commit the files it needs.

Everything else is yours.
Each prompt ends with a marker line that you replace with your own writing; `uv run p2 check --final` fails while one is left.
Write what you measured, including what did not work.
What I read for is whether each claim matches its interval, not whether the result is good news.

Words used below: recall@10, MRR@10 and nDCG@10 are the three scores, each averaged over the queries of a set; step 7 of stage 1 in the README defines them, and lecture 14 goes deeper.
A paired interval is the 95% interval of the mean difference between two systems on the same queries, found by resampling the queries 10,000 times.
When an interval includes zero, the gold set cannot tell the two systems apart, and the right words are "not distinguishable on this gold set".
The minimum detectable difference is the smallest gap this many queries could reliably show, so a difference below it is invisible to this gold set, not absent.

---

## 1. Stage 1 - the shared corpus (30 CFR Chapter I)

### What you built

For each of `dense`, `hybrid` and `rerank`, one or two sentences: the embedding model, how documents were chunked, what was fused and how, how many candidates the reranker saw, and anything you changed from the 12 and 13 lab code.

Dense:Uses bge-small-en-v1.5, documents were chunked into 300-word chunks with 50 words of overlap, and scored by cosine similarity. An article scores as its best chunk and there are no changes from lab 12 except working on chunks instead of whole articles.
Hybrid: Uses a reciptrocal rank fusion of bm25 and dense with k=60 over full rankings. The only change from lab 13 is bm25 results with score 0 are dropped.
Rerank: Uses claude sonnet to reorder 20 canidates interleaved from bm25 and dense's rankings. Each canidate is shown as its title and best-fit chunk. The changes from lab 13 were the canidates came from bm25 and dense interleaved and not hybrid and that it is the best fitting chunk instead of the first 600 characters.

### Practice queries (20)

Scores per system.

<!-- p2:begin shared-practice -->
| System | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| bm25 | 0.625 | 0.507 | 0.518 |
| dense | 0.558 | 0.562 | 0.480 |
| hybrid | 0.617 | 0.471 | 0.456 |
| rerank | 0.833 | 0.900 | 0.846 |
| rerank_c10 | 0.817 | 0.900 | 0.838 |

20 judged queries; nDCG uses binary labels; a random ranking of the 2,484 documents would get recall@10 near 0.004.
<!-- p2:end shared-practice -->

The same scores per query class.

<!-- p2:begin shared-practice-classes -->
| System | Metric | identifier (n=7) | paraphrase (n=7) | mixed (n=6) |
| --- | --- | ---: | ---: | ---: |
| bm25 | Recall@10 | 1.000 | 0.000 | 0.917 |
| bm25 | MRR@10 | 0.810 | 0.000 | 0.746 |
| bm25 | nDCG@10 | 0.857 | 0.000 | 0.728 |
| dense | Recall@10 | 0.214 | 0.595 | 0.917 |
| dense | MRR@10 | 0.333 | 0.714 | 0.653 |
| dense | nDCG@10 | 0.211 | 0.593 | 0.661 |
| hybrid | Recall@10 | 0.571 | 0.405 | 0.917 |
| hybrid | MRR@10 | 0.514 | 0.152 | 0.792 |
| hybrid | nDCG@10 | 0.435 | 0.202 | 0.779 |
| rerank | Recall@10 | 1.000 | 0.595 | 0.917 |
| rerank | MRR@10 | 1.000 | 0.714 | 1.000 |
| rerank | nDCG@10 | 0.989 | 0.626 | 0.936 |
| rerank_c10 | Recall@10 | 1.000 | 0.548 | 0.917 |
| rerank_c10 | MRR@10 | 1.000 | 0.714 | 1.000 |
| rerank_c10 | nDCG@10 | 1.000 | 0.592 | 0.936 |
<!-- p2:end shared-practice-classes -->

Differences between every pair of systems, each with its paired interval and the minimum detectable difference.

<!-- p2:begin shared-practice-pairs -->
| Comparison | Metric | Mean difference | 95% interval | MDD | Reading |
| --- | --- | ---: | ---: | ---: | --- |
| dense minus bm25 | Recall@10 | -0.067 | [-0.350, +0.225] | 0.415 | not distinguishable |
| dense minus bm25 | MRR@10 | +0.055 | [-0.225, +0.343] | 0.412 | not distinguishable |
| dense minus bm25 | nDCG@10 | -0.039 | [-0.302, +0.231] | 0.385 | not distinguishable |
| hybrid minus bm25 | Recall@10 | -0.008 | [-0.225, +0.208] | 0.317 | not distinguishable |
| hybrid minus bm25 | MRR@10 | -0.037 | [-0.178, +0.083] | 0.192 | not distinguishable |
| hybrid minus bm25 | nDCG@10 | -0.062 | [-0.218, +0.082] | 0.218 | not distinguishable |
| hybrid minus dense | Recall@10 | +0.058 | [-0.117, +0.242] | 0.261 | not distinguishable |
| hybrid minus dense | MRR@10 | -0.092 | [-0.306, +0.109] | 0.301 | not distinguishable |
| hybrid minus dense | nDCG@10 | -0.023 | [-0.193, +0.137] | 0.240 | not distinguishable |
| rerank minus bm25 | Recall@10 | +0.208 | [+0.050, +0.383] | 0.242 | rerank higher |
| rerank minus bm25 | MRR@10 | +0.393 | [+0.200, +0.595] | 0.287 | rerank higher |
| rerank minus bm25 | nDCG@10 | +0.327 | [+0.161, +0.504] | 0.250 | rerank higher |
| rerank minus dense | Recall@10 | +0.275 | [+0.100, +0.450] | 0.259 | rerank higher |
| rerank minus dense | MRR@10 | +0.338 | [+0.150, +0.533] | 0.273 | rerank higher |
| rerank minus dense | nDCG@10 | +0.366 | [+0.204, +0.537] | 0.242 | rerank higher |
| rerank minus hybrid | Recall@10 | +0.217 | [+0.067, +0.392] | 0.235 | rerank higher |
| rerank minus hybrid | MRR@10 | +0.429 | [+0.247, +0.614] | 0.266 | rerank higher |
| rerank minus hybrid | nDCG@10 | +0.389 | [+0.241, +0.546] | 0.220 | rerank higher |
| rerank_c10 minus bm25 | Recall@10 | +0.192 | [+0.050, +0.358] | 0.223 | rerank_c10 higher |
| rerank_c10 minus bm25 | MRR@10 | +0.393 | [+0.200, +0.595] | 0.287 | rerank_c10 higher |
| rerank_c10 minus bm25 | nDCG@10 | +0.320 | [+0.163, +0.487] | 0.236 | rerank_c10 higher |
| rerank_c10 minus dense | Recall@10 | +0.258 | [+0.083, +0.450] | 0.270 | rerank_c10 higher |
| rerank_c10 minus dense | MRR@10 | +0.338 | [+0.150, +0.533] | 0.273 | rerank_c10 higher |
| rerank_c10 minus dense | nDCG@10 | +0.358 | [+0.188, +0.537] | 0.254 | rerank_c10 higher |
| rerank_c10 minus hybrid | Recall@10 | +0.200 | [+0.067, +0.358] | 0.216 | rerank_c10 higher |
| rerank_c10 minus hybrid | MRR@10 | +0.429 | [+0.247, +0.614] | 0.266 | rerank_c10 higher |
| rerank_c10 minus hybrid | nDCG@10 | +0.381 | [+0.240, +0.527] | 0.208 | rerank_c10 higher |
| rerank_c10 minus rerank | Recall@10 | -0.017 | [-0.050, +0.000] | 0.047 | not distinguishable |
| rerank_c10 minus rerank | MRR@10 | +0.000 | [+0.000, +0.000] | - | identical on every query |
| rerank_c10 minus rerank | nDCG@10 | -0.008 | [-0.035, +0.012] | 0.035 | not distinguishable |

The interval is a paired bootstrap (10,000 resamples of the queries); MDD is the smallest difference this many queries detect 80% of the time. Two systems that score the same on every query have no interval to speak of, so their MDD is shown as -.
<!-- p2:end shared-practice-pairs -->

The 40 test queries have no answer key in this repo.
Your test run files are scored by the course and the score comes back to you as feedback, so nothing goes here for them.

### What the intervals let you claim

Which differences are distinguishable from zero and which are not?
What is the minimum detectable difference at 20 queries, and what does that say about any gap smaller than it?
Which claim from lecture 12 or 13 did your numbers support, and which did they leave open?

The difference between rerank and bm25, dense, and hybrid are all distinguishable from zero. The difference between dense and bm25, hybrid and bm25, and hybrid and dense are not distinguishable from zero.  The minimal detectable difference at 20 queries ranges from 0.192 to 0.412 depending on the pair. Any gap smaller than the MDD would not be distinguishable. My numbers support the claim from lecture 12 that no retriever wins everywhere, because bm25 wins on identifier queries and dense wins on paraphrase queries. Also, they support the claim from lab 13 that a reranker helps, the accuracy of retrieval, because the reranker consistently outperformed the the methods without one. My numbers leave the claim from lecture 14 that fusion typically beats just bm25 and dense, because the gap was not distinguishable from zero.

---

## 2. Stage 1 - cited answers on the 12 shared questions

<!-- p2:begin answers -->
| Label | System | Verified (in) | 95% interval | not_found (in) | Declined (out) | 95% interval | Quotes found |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| rerank | rerank | 7 of 8 (88%) | [0.529, 0.978] | 1 of 8 (12%) | 4 of 4 (100%) | [0.510, 1.000] | 11 of 11 |
<!-- p2:end answers -->

Which system answered, and why that one?
What did you change in `prompts/answer.txt`, if anything, and did the verified share or the declined share move?

Then read three in-corpus answers that `uv run p2 verify` passed.
For each one, open the cited chunk and say whether the quote really supports the claim next to it.
The check proves a quote is a real piece of the chunk and cannot prove that it supports the claim, so this reading is the part only you can do.

TODO: write your answer choices and your three-answer audit.

---

## 3. Stage 2 - your corpus and your gold set

### The corpus

What is it, where did it come from, how many documents and how many megabytes, and what is the license basis for publishing it?
Name the one or two documents you were least sure about and what you decided.
Say which of the allowed sources in the brief it comes from.

My corpus is 601 articles on dog-breeds from wikipedia (wikipedia is an allowed source in the breif), it is 3.3 megabytes, and the license is CC BY-SA 4.0. The document I was least sure about was the dingo, which is an animal that is arguably a type of dog, but is not a dog breed in a traditional sense. I decided to keep the dingo in the corpus, because I believe it is relevant enough, due to dingos being the descendants of domestic dogs.

### The gold set

How many queries, how many with origin `hand` and how many with origin `claude`, and which query classes did you use and why?
How did you decide that a document is relevant: write your relevance rule in two or three sentences, the way the brief does for the shared corpus.
How did you find candidates (the systems' top 10, a keyword search, reading), and did you read every document before you labeled it?
Your labels are binary (`rel` 1) unless you say otherwise: if you use graded labels, declare the scale here, for example 2 means the document answers the query fully and 1 means it helps.
TODO: still needs to be finished
There are 30 queries, 10 of which with the origin 'hand' and 20 with the origin 'claude'. Query Classes go here! An article is considered relevant if it states the dog breed has a trait which is asked for in the query (unless the question specifically asks for it, saying a dog has the highest trait in its weight class or region is not enough to be relevant). Several answers can be relevent unless the question only has one right answer (if a question is ambiguous, multiple answers can be given, even if it is a question that asks for one right answer). Unless the question overtly asks for one or the other average and the record held by one dog both count, for example the smallest dog question can be answered by chihuahua (the smallest on average) and yorkshire terrier (the smallest recorded).

---

## 4. Stage 2 - results on your corpus

Scores per system on your gold set.

<!-- p2:begin own -->
| System | Recall@10 | MRR@10 | nDCG@10 |
| --- | ---: | ---: | ---: |
| bm25 | 0.710 | 0.707 | 0.654 |
| dense | 0.686 | 0.675 | 0.654 |
| hybrid | 0.757 | 0.741 | 0.709 |
| rerank | 0.810 | 0.890 | 0.820 |
| ablation/hybrid_k10 | 0.761 | 0.762 | 0.720 |

30 judged queries; nDCG uses binary labels; a random ranking of the 601 documents would get recall@10 near 0.017.
<!-- p2:end own -->

The same scores per query class.

<!-- p2:begin own-classes -->
| System | Metric | paraphrase (n=17) | mixed (n=6) | identifier (n=7) |
| --- | --- | ---: | ---: | ---: |
| bm25 | Recall@10 | 0.567 | 0.833 | 0.952 |
| bm25 | MRR@10 | 0.647 | 0.617 | 0.929 |
| bm25 | nDCG@10 | 0.542 | 0.681 | 0.905 |
| dense | Recall@10 | 0.494 | 0.861 | 1.000 |
| dense | MRR@10 | 0.517 | 0.742 | 1.000 |
| dense | nDCG@10 | 0.477 | 0.766 | 0.990 |
| hybrid | Recall@10 | 0.620 | 0.917 | 0.952 |
| hybrid | MRR@10 | 0.622 | 0.778 | 1.000 |
| hybrid | nDCG@10 | 0.563 | 0.819 | 0.966 |
| rerank | Recall@10 | 0.694 | 0.917 | 1.000 |
| rerank | MRR@10 | 0.806 | 1.000 | 1.000 |
| rerank | nDCG@10 | 0.705 | 0.936 | 1.000 |
| ablation/hybrid_k10 | Recall@10 | 0.607 | 0.917 | 1.000 |
| ablation/hybrid_k10 | MRR@10 | 0.661 | 0.771 | 1.000 |
| ablation/hybrid_k10 | nDCG@10 | 0.578 | 0.810 | 0.986 |
<!-- p2:end own-classes -->

The same scores for the queries you wrote yourself (`hand`) and the ones a model drafted (`claude`), with the difference between the two groups and its interval.
Once both groups have queries, the table also says whether `bm25`'s lead over `dense` differs between them, and what share of each query's content words its best relevant document contains, which is stretch option 6.

<!-- p2:begin own-origins -->
| System | Metric | hand (n=10) | claude (n=20) | hand minus claude | 95% interval | Reading |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| bm25 | Recall@10 | 0.258 | 0.936 | -0.677 | [-0.898, -0.404] | claude higher |
| bm25 | MRR@10 | 0.400 | 0.860 | -0.460 | [-0.760, -0.125] | claude higher |
| bm25 | nDCG@10 | 0.286 | 0.838 | -0.552 | [-0.789, -0.276] | claude higher |
| dense | Recall@10 | 0.421 | 0.818 | -0.396 | [-0.670, -0.108] | claude higher |
| dense | MRR@10 | 0.442 | 0.791 | -0.350 | [-0.666, -0.006] | claude higher |
| dense | nDCG@10 | 0.401 | 0.781 | -0.380 | [-0.669, -0.067] | claude higher |
| hybrid | Recall@10 | 0.493 | 0.889 | -0.396 | [-0.641, -0.154] | claude higher |
| hybrid | MRR@10 | 0.442 | 0.891 | -0.450 | [-0.715, -0.166] | claude higher |
| hybrid | nDCG@10 | 0.396 | 0.865 | -0.469 | [-0.702, -0.215] | claude higher |
| rerank | Recall@10 | 0.505 | 0.963 | -0.458 | [-0.674, -0.237] | claude higher |
| rerank | MRR@10 | 0.720 | 0.975 | -0.255 | [-0.540, +0.000] | not distinguishable |
| rerank | nDCG@10 | 0.548 | 0.956 | -0.408 | [-0.639, -0.184] | claude higher |
| ablation/hybrid_k10 | Recall@10 | 0.480 | 0.901 | -0.421 | [-0.646, -0.190] | claude higher |
| ablation/hybrid_k10 | MRR@10 | 0.496 | 0.895 | -0.399 | [-0.677, -0.105] | claude higher |
| ablation/hybrid_k10 | nDCG@10 | 0.419 | 0.870 | -0.451 | [-0.685, -0.196] | claude higher |

The hand and claude queries are different queries, so the interval of hand minus claude comes from resampling the queries within each group (10,000 times), not from pairing them.

Do model-written queries favor keyword search? bm25's lead over dense (bm25 minus dense, per query) on the claude queries and on the hand queries, and claude minus hand:

| Metric | Lead on claude | Lead on hand | Claude minus hand | 95% interval | Reading |
| --- | ---: | ---: | ---: | ---: | --- |
| Recall@10 | +0.118 | -0.163 | +0.281 | [+0.033, +0.541] | bm25 gains more on claude queries |
| MRR@10 | +0.069 | -0.042 | +0.110 | [-0.332, +0.542] | not distinguishable |
| nDCG@10 | +0.057 | -0.115 | +0.172 | [-0.111, +0.470] | not distinguishable |

Mean content-word overlap, the share of a query's content words found in its best relevant document: hand 0.85 (10 queries), claude 0.88 (20 queries).

Stretch option 6 asks for at least 20 judged queries of each origin; here there are 10 hand and 20 claude.
<!-- p2:end own-origins -->

Differences between every pair of systems.

<!-- p2:begin own-pairs -->
| Comparison | Metric | Mean difference | 95% interval | MDD | Reading |
| --- | --- | ---: | ---: | ---: | --- |
| dense minus bm25 | Recall@10 | -0.024 | [-0.149, +0.096] | 0.177 | not distinguishable |
| dense minus bm25 | MRR@10 | -0.032 | [-0.209, +0.146] | 0.261 | not distinguishable |
| dense minus bm25 | nDCG@10 | +0.0002 | [-0.131, +0.132] | 0.192 | not distinguishable |
| hybrid minus bm25 | Recall@10 | +0.047 | [-0.041, +0.137] | 0.130 | not distinguishable |
| hybrid minus bm25 | MRR@10 | +0.035 | [-0.103, +0.174] | 0.201 | not distinguishable |
| hybrid minus bm25 | nDCG@10 | +0.054 | [-0.031, +0.140] | 0.124 | not distinguishable |
| hybrid minus dense | Recall@10 | +0.071 | [+0.001, +0.146] | 0.106 | hybrid higher |
| hybrid minus dense | MRR@10 | +0.067 | [-0.009, +0.154] | 0.118 | not distinguishable |
| hybrid minus dense | nDCG@10 | +0.054 | [-0.015, +0.127] | 0.102 | not distinguishable |
| rerank minus bm25 | Recall@10 | +0.100 | [+0.035, +0.179] | 0.105 | rerank higher |
| rerank minus bm25 | MRR@10 | +0.183 | [+0.033, +0.343] | 0.223 | rerank higher |
| rerank minus bm25 | nDCG@10 | +0.166 | [+0.075, +0.267] | 0.139 | rerank higher |
| rerank minus dense | Recall@10 | +0.124 | [+0.047, +0.221] | 0.128 | rerank higher |
| rerank minus dense | MRR@10 | +0.215 | [+0.094, +0.348] | 0.185 | rerank higher |
| rerank minus dense | nDCG@10 | +0.166 | [+0.078, +0.263] | 0.136 | rerank higher |
| rerank minus hybrid | Recall@10 | +0.053 | [-0.012, +0.122] | 0.098 | not distinguishable |
| rerank minus hybrid | MRR@10 | +0.149 | [+0.044, +0.274] | 0.166 | rerank higher |
| rerank minus hybrid | nDCG@10 | +0.111 | [+0.048, +0.181] | 0.098 | rerank higher |
| ablation/hybrid_k10 minus bm25 | Recall@10 | +0.051 | [-0.031, +0.143] | 0.125 | not distinguishable |
| ablation/hybrid_k10 minus bm25 | MRR@10 | +0.055 | [-0.069, +0.184] | 0.184 | not distinguishable |
| ablation/hybrid_k10 minus bm25 | nDCG@10 | +0.065 | [-0.016, +0.155] | 0.124 | not distinguishable |
| ablation/hybrid_k10 minus dense | Recall@10 | +0.075 | [+0.022, +0.142] | 0.088 | ablation/hybrid_k10 higher |
| ablation/hybrid_k10 minus dense | MRR@10 | +0.087 | [-0.002, +0.192] | 0.142 | not distinguishable |
| ablation/hybrid_k10 minus dense | nDCG@10 | +0.065 | [+0.007, +0.130] | 0.090 | ablation/hybrid_k10 higher |
| ablation/hybrid_k10 minus hybrid | Recall@10 | +0.004 | [-0.048, +0.056] | 0.077 | not distinguishable |
| ablation/hybrid_k10 minus hybrid | MRR@10 | +0.021 | [-0.006, +0.061] | 0.050 | not distinguishable |
| ablation/hybrid_k10 minus hybrid | nDCG@10 | +0.011 | [-0.017, +0.041] | 0.042 | not distinguishable |
| ablation/hybrid_k10 minus rerank | Recall@10 | -0.049 | [-0.094, -0.013] | 0.060 | rerank higher |
| ablation/hybrid_k10 minus rerank | MRR@10 | -0.128 | [-0.256, -0.011] | 0.179 | rerank higher |
| ablation/hybrid_k10 minus rerank | nDCG@10 | -0.100 | [-0.163, -0.042] | 0.088 | rerank higher |

The interval is a paired bootstrap (10,000 resamples of the queries); MDD is the smallest difference this many queries detect 80% of the time.
<!-- p2:end own-pairs -->

Which differences are distinguishable and which are not, at your gold-set size?
Do the `hand` queries and the `claude` queries tell the same story?
Did your prediction in `DECISIONS.md` prompt 1 hold?

TODO: write what your own-corpus intervals let you claim.

---

## 5. The ablation

Change one thing and keep everything else the same.
Write your hypothesis here before you run it, in one sentence with a direction: "I expect X to raise MRR@10 on my corpus because Y."

I expect changing the fusion setting to k=10 will improve the MRR@10 on my corpus, because most of the gold set questions only have 1 or very few answers, so it would be better to favor the top few articles during fusion.
The run file for it lives in `runs/own/ablation/`.

<!-- p2:begin own-ablation -->
| Comparison | Metric | Mean difference | 95% interval | MDD | Reading |
| --- | --- | ---: | ---: | ---: | --- |
| ablation/hybrid_k10 minus bm25 | Recall@10 | +0.051 | [-0.031, +0.143] | 0.125 | not distinguishable |
| ablation/hybrid_k10 minus bm25 | MRR@10 | +0.055 | [-0.069, +0.184] | 0.184 | not distinguishable |
| ablation/hybrid_k10 minus bm25 | nDCG@10 | +0.065 | [-0.016, +0.155] | 0.124 | not distinguishable |
| ablation/hybrid_k10 minus dense | Recall@10 | +0.075 | [+0.022, +0.142] | 0.088 | ablation/hybrid_k10 higher |
| ablation/hybrid_k10 minus dense | MRR@10 | +0.087 | [-0.002, +0.192] | 0.142 | not distinguishable |
| ablation/hybrid_k10 minus dense | nDCG@10 | +0.065 | [+0.007, +0.130] | 0.090 | ablation/hybrid_k10 higher |
| ablation/hybrid_k10 minus hybrid | Recall@10 | +0.004 | [-0.048, +0.056] | 0.077 | not distinguishable |
| ablation/hybrid_k10 minus hybrid | MRR@10 | +0.021 | [-0.006, +0.061] | 0.050 | not distinguishable |
| ablation/hybrid_k10 minus hybrid | nDCG@10 | +0.011 | [-0.017, +0.041] | 0.042 | not distinguishable |
| ablation/hybrid_k10 minus rerank | Recall@10 | -0.049 | [-0.094, -0.013] | 0.060 | rerank higher |
| ablation/hybrid_k10 minus rerank | MRR@10 | -0.128 | [-0.256, -0.011] | 0.179 | rerank higher |
| ablation/hybrid_k10 minus rerank | nDCG@10 | -0.100 | [-0.163, -0.042] | 0.088 | rerank higher |

The interval is a paired bootstrap (10,000 resamples of the queries); MDD is the smallest difference this many queries detect 80% of the time.
<!-- p2:end own-ablation -->

The queries your ablation helped and hurt, against the system it varies, by reciprocal rank.
`p2 score` finds that system from a line such as `BASE = "bm25"` in your variant's file, or else from its name: `bm25_lab` varies `bm25`.

<!-- p2:begin own-ablation-queries -->
ablation/hybrid_k10 against hybrid (BASE = "hybrid" in p2/retrievers/hybrid_k10.py): it helped 3 queries, hurt 2 and left 25 unchanged.

| Query | Class | Origin | hybrid RR | ablation/hybrid_k10 RR | Change | Effect |
| --- | --- | --- | ---: | ---: | ---: | --- |
| h07 | paraphrase | hand | 0.500 | 1.000 | +0.500 | helped |
| h08 | paraphrase | hand | 0.000 | 0.167 | +0.167 | helped |
| c14 | paraphrase | claude | 0.125 | 0.200 | +0.075 | helped |
| h03 | paraphrase | hand | 0.250 | 0.167 | -0.083 | hurt |
| h02 | mixed | hand | 0.167 | 0.125 | -0.042 | hurt |

RR is the reciprocal rank of the first relevant document in the top 10 (0 when none is there), the per-query value behind MRR@10; the queries at the top of each list are the ones to read.
<!-- p2:end own-ablation-queries -->

What did you change, what happened, and does the interval support the claim you want to make?
If the result is not distinguishable, say what size of effect your gold set could have seen.
Read the queries at the top of each list in the second table, and say whether your change explains them.

I will change the fusion setting. I expect changing the fusion setting to k=10 will improve the MRR@10 on my corpus, because most of the gold set questions only have 1 or very few answers, so it would be better to favor the top few articles during fusion.

---

## 6. Failure analysis

Pick the queries where your best system on your own corpus failed: the relevant document is missing from the top 10, or sits far below the top.
Take at least five, and read what the system returned next to what was relevant.
Then sort the failures by cause, for example a vocabulary mismatch, near-duplicate documents, a chunk that cut the answer in half, a query that is ambiguous, or a label that was wrong, because sometimes the gold set is what failed.

| qid | what the best system returned | what was relevant | cause | what you would try |
|---|---|---|---|---|

TODO: add one row for each failure you analyzed, and write two or three sentences on the pattern you see across them.

---

## 7. Cross-corpus comparison

The two tables to compare are the shared-corpus scores in section 1 and your own-corpus scores in section 4, with their intervals.
If you want them side by side, copy the rows you need into a table here and say that you copied them.

Did the winner change between the shared corpus and yours?
Why, or why not: what is different about the two collections (document length, vocabulary, identifiers, near-duplicates, how the queries were written), and which of your explanations did you test and which are guesses?
Say what 20 queries on one side and your gold-set size on the other cannot support.

TODO: write the cross-corpus comparison.

---

## 8. Stretch

498E: the stretch is one of the six options in the brief's "One stretch" section, and that section says what earns the 25 points for each.
It is optional, so `uv run p2 check --final` never waits on this section.
598E: the rider is your stretch, so write "rider" below and put its results in section 9; the other options add no points, because the project is capped at 150.

Whichever option you chose, write these five things:

1. The option's name.
2. What you did, and the files that hold it.
3. The table `p2 score` wrote for it, by name: one of the three below, `own-ablation` and `own-ablation-queries` in section 5 for a second ablation, `own-origins` in section 4 for the hand and claude queries, or `repeats` in section 9 for the rider.
4. What its interval lets you claim, and what it does not.
5. One thing you would do next, and what result would tell you it worked.

For a second ablation, write its hypothesis here before you run it, and commit it, so your history shows that it came first.
For the hand and claude queries, do the same with your prediction before you score.

### Claim-level faithfulness check (option 2)

Claude's verdicts from `p2 judge` against your own verdicts in the calibration file.

<!-- p2:begin stretch-judge -->
_No judged answers yet (stretch option 2): `uv run p2 judge answers/shared/LABEL.json` writes them, your own verdicts go in answers/shared/LABEL.calibration.tsv, and then `uv run p2 score` fills this table._
<!-- p2:end stretch-judge -->

### Cost and latency (option 3)

The Claude calls, tokens and seconds in every trace you committed, and what a cheaper system or answers file saves against what it loses.

<!-- p2:begin stretch-cost -->
Every trace in traces/ that records a Claude call:

| Trace | System | Spans | Claude calls | Saved | Input tokens | Output tokens | Seconds | Input per span | Output per span | Seconds per span |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| traces/answers-rerank.jsonl | rerank | 12 | 24 | 4 | 291,214 | 4,602 | 94.5 | 24,268 | 384 | 7.9 |
| traces/own-own-rerank.jsonl | rerank | 30 | 30 | 2 | 535,266 | 2,730 | 126.9 | 17,842 | 91 | 4.2 |
| traces/shared-practice-rerank.jsonl | rerank | 20 | 20 | 20 | 307,870 | 2,044 | 96.0 | 15,394 | 102 | 4.8 |
| traces/shared-practice-rerank_c10.jsonl | rerank_c10 | 20 | 20 | 2 | 213,880 | 1,420 | 80.1 | 10,694 | 71 | 4.0 |
| traces/shared-test-rerank.jsonl | rerank | 40 | 40 | 40 | 600,000 | 3,972 | 205.4 | 15,000 | 99 | 5.1 |

A span is one query of a run, one question of an answers file, or one claim of a judged file. A saved reply costs nothing now, so it counts the tokens and the seconds of the call that made it.

Every pair of systems on the same queries where at least one calls Claude, the one with fewer Claude input tokens per query first:

| Cheaper minus dearer | Queries | MRR@10 difference | 95% interval | Input tokens saved per query | Seconds saved per query | Reading |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| shared practice: bm25 minus rerank | 20 | -0.393 | [-0.595, -0.200] | 15,394 | 4.8 | rerank higher |
| shared practice: dense minus rerank | 20 | -0.338 | [-0.533, -0.150] | 15,394 | 4.8 | rerank higher |
| shared practice: hybrid minus rerank | 20 | -0.429 | [-0.614, -0.247] | 15,394 | 4.8 | rerank higher |
| shared practice: bm25 minus rerank_c10 | 20 | -0.393 | [-0.595, -0.200] | 10,694 | 4.0 | rerank_c10 higher |
| shared practice: dense minus rerank_c10 | 20 | -0.338 | [-0.533, -0.150] | 10,694 | 4.0 | rerank_c10 higher |
| shared practice: hybrid minus rerank_c10 | 20 | -0.429 | [-0.614, -0.247] | 10,694 | 4.0 | rerank_c10 higher |
| shared practice: rerank_c10 minus rerank | 20 | +0.000 | [+0.000, +0.000] | 4,700 | 0.8 | identical on every query |
| own: bm25 minus rerank | 30 | -0.183 | [-0.343, -0.033] | 17,842 | 4.2 | rerank higher |
| own: dense minus rerank | 30 | -0.215 | [-0.348, -0.094] | 17,842 | 4.2 | rerank higher |
| own: hybrid minus rerank | 30 | -0.149 | [-0.274, -0.044] | 17,842 | 4.2 | rerank higher |

The difference is the cheaper system's score minus the dearer one's, with its paired interval; the savings count Claude calls only, so a system that makes none saves all of the other's.

Systems that do not call Claude, from traces/retrieval/ on the machine that last ran `p2 score` (git ignores that folder, so `p2 check` does not compare this part):

| Trace | System | Queries | Seconds | Milliseconds per query |
| --- | --- | ---: | ---: | ---: |
| traces/retrieval/own-own-ablation-hybrid_k10.jsonl | hybrid_k10 | 30 | 0.14 | 4.7 |
| traces/retrieval/own-own-bm25.jsonl | bm25 | 30 | 0.04 | 1.3 |
| traces/retrieval/own-own-dense.jsonl | dense | 30 | 0.09 | 2.9 |
| traces/retrieval/own-own-hybrid.jsonl | hybrid | 30 | 0.15 | 5.1 |
| traces/retrieval/shared-practice-bm25.jsonl | bm25 | 20 | 0.04 | 1.9 |
| traces/retrieval/shared-practice-dense.jsonl | dense | 20 | 0.10 | 5.2 |
| traces/retrieval/shared-practice-hybrid.jsonl | hybrid | 20 | 0.17 | 8.3 |
| traces/retrieval/shared-test-bm25.jsonl | bm25 | 40 | 0.06 | 1.5 |
| traces/retrieval/shared-test-dense.jsonl | dense | 40 | 0.18 | 4.5 |
| traces/retrieval/shared-test-hybrid.jsonl | hybrid | 40 | 0.33 | 8.2 |
<!-- p2:end stretch-cost -->

### The grep agent (option 5)

Your stretch run on some of your own queries against the four systems on the same queries.

<!-- p2:begin stretch-agent -->
_No stretch runs yet (stretch option 5): `uv run p2 run --corpus own --queries eval/own/agent.queries.tsv --system agent --stretch` writes one to runs/own/stretch/, then `uv run p2 score` fills this table._
<!-- p2:end stretch-agent -->

### Your stretch

Write the five things here.

---

## 9. 598E only - repeats and the pre-registered claim

498E students can leave this section as it is; nothing checks it.
598E students replace each line that starts with "598E: write", and `uv run p2 check --final` counts those lines as work still to do until they are gone.

### Repeats on the shared corpus

Three runs of the reranker on the practice queries, and three answers files, with their run-to-run spread and Wilson intervals.

<!-- p2:begin repeats -->
_No repeated runs or answers files yet (598E: `p2 run ... --repeat 3` and `p2 answer ... --repeat 3`)._
<!-- p2:end repeats -->

Does the reranker's gain over its first stage survive the run-to-run variation?
Write what the spread is, how it compares with the gain, and what the Wilson intervals on the verified share and the declined share say about 8 and 4 questions.

598E: write the repeats result here.

### The pre-registered claim

The claim, the smallest effect, the gold-set size and the test are in `PREREG.md`, committed before your own gold-set judgments.
Here, say whether you followed the plan, what the interval turned out to be, and what that means.
The outcome section of `PREREG.md` holds the short version.

598E: write the claim and its outcome here.
