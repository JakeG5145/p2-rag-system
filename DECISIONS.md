# Decision log

Your methods section, in your own words.
About one to two pages in total.

Answer these as you go, not the night before it is due.
Each answer is easier to write while the decision is still fresh, and prompt 1 only works if you write it before you see your own-corpus numbers.
Specifics beat polish: a short, honest answer with a number in it is worth more than a long vague one.

Each prompt ends with a marker line.
Replace that line with your answer.
`uv run p2 check` reports a marker as unfinished work, and `uv run p2 check --final` fails while any marker is left, so a finished log is part of being done.

Please do not let the agent write these for you.
These answers are about what you chose and what you knew, and the agent cannot know that.
Prompt 3 in particular only works in your own words.

---

## 1. Why this corpus, and what you expected

Why did you pick the corpus you used in stage 2, and why does it belong to a field or a question you care about?
Then say what you expected before you measured anything: which of `bm25`, `dense`, `hybrid` and `rerank` do you think will win on it, and which will do worst, and why?

Commit this answer before your first `uv run p2 score` on the own corpus.
Git history then shows that the expectation came first, which is what lets it be wrong in a way that teaches you something.
If you were surprised later, say so in prompt 4 or in EVAL.md; do not come back and rewrite this one.

I chose the wikipedia articles of dog breeds as my corpus, because I love dogs and want to learn more about them. I think rerank will win, because it gives a much more nuanced score on a documents relevency compared to the other methods. I think bm25 will do worst, because it just looks for keywords which might not always properly answer the question.

---

## 2. A fork in the road

Name one real design choice where you could have gone two ways: the chunk size, the embedding model, how the two systems are fused, how many documents the reranker sees, a sentence in `prompts/answer.txt`, how you cleaned the corpus.

Say which you picked, what the alternative was, and what you gave up by not taking it.
If you measured both, give both numbers.
If you rejected the alternative without measuring it, say why that was a fair call, and what it cost you in time, tokens or complexity.

"There was no alternative" is not an answer.
Find the fork.

I chose to give the reranker a combination of bm25 and dense's top candidates instead of giving it hybrid's top candidates. I chose this, because the practice queries gave really poor results from hybrid due to poor dense results throwing off the more accurate bm25 results, so I decided to use this method to hedge against that issue. By taking this option, I gave up using the hybrid candidates for the reranker, which could be more accurate for some queries. I did not measure both options for my corpus, only the practice corpus, because it would have required me to run several more claude calls when I was limited on usage. I believe it was reasonable to reject the alternative because a combination of bm25 and dense performed far better in the practice queries compared to hybrid (on the practice queries bm25+dense resulted in 18/20 correct answers being in the top 20 candidates while hybrid only gave 15/20).

---

## 3. Where you overruled the agent

One time Claude suggested, wrote or claimed something and you did not take it.
It might be a relevance judgment you disagreed with, a retriever it called finished when a run file showed otherwise, a number it summarized wrongly, or a license it said was fine.

What did it do?
How did you notice?
What did you do instead?

If it genuinely never happened, say so plainly, and then say what you would have had to check in order to notice.
Being honest here costs you far less than a story you cannot defend when you record your video.

When claude was writing its part of the gold set it wrote almost all of its questions as very obvious descriptions of a single dog breed, but I wanted my gold set to have a few more open ended queries. I noticed this by reading its queries after it wrote them. I gave the AI my preferences and had it rewrite some of them, then I read the new ones to ensure they met my preferences.

---

## 4. A number you do not trust

Pick one number in `EVAL.md` that you do not fully trust, and say why.
It could be a mean over a small query class, a difference whose interval includes zero, a verified share of 100%, a score on a gold set you wrote yourself, or a result you got only once.

What would have to be true for you to trust it?
Did you do anything to test it, and what did that show?

I do not fully trust the 1.0 MRR on rerank for the identifier and mixed class practice queries, because claude will give different answers every time and it is not likely to always answer correctly. I would have to run many trials all of which result in a 1.0 MRR to trust it. I did not test it to avoid using too many claude calls, because to fully confirm this number I would need to make a lot of calls.

---

## 5. What is still wrong

One thing in your system, your corpus or your gold set that is not right, not finished, or that you do not fully understand.

What would you do next, and how would you find out whether it matters?
Name the file, the query or the document where someone could look.

In my gold-set I misspelled lifeguard as life guard, by the time I caught this issue I had already done most of the assignment and would have had to redo a large portion of it with how it would have changed the data. If I had more time I would redo it to remove this typo, but it does introduce some interesting data of how a minor typo can greatly change the accuracy of a RAG system. I could find out if it mattered by checking if the accuracy on that question improved when the typo was fixed. It is in eval/own/queries.tsv in query h10.
