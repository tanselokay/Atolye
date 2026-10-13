# Principles

The five rules the whole thing is built toward. They are choices, not defaults — each one costs
something, and each one is the reason the project is worth doing at all.

## 1. The machine drafts; a human decides

A local model does the heavy lifting — reading hundreds of articles, shortlisting, writing a first
headline and a "why it matters". But nothing reaches a reader unless a person chose it. The most
valuable work is the human's: deciding what matters, fixing wording, and checking a claim against
its source. A machine that also *decides* is not a publication; it's a spam feed.

## 2. All AI runs locally

Every model runs on the maker's own hardware — no cloud AI service, no API keys, no per-article
cost, and the source material never leaves the machine. A few years ago this needed the cloud;
today a resident ~27–32B model does the daily editorial work well. Local-first is privacy,
independence, and a near-zero marginal cost, all at once.

## 3. Honest about the machine

A page says plainly what a model wrote and what a human did not review. "This critique was written
by a local model and is not checked line by line" does not reduce trust — it earns it. The reader
should always know which words are the machine's.

## 4. Accessible to everyone

Semantic headings, real alt text, keyboard and screen-reader support, AA contrast, readable on a
phone. Not for SEO — because a publication that some people can't read is not finished.

## 5. Respect other people's work

Link out to the original; never re-host someone else's article. Media is hotlinked or embedded and
credited, not copied. This is both an ethic and the safe side of copyright.

---

Two habits that keep the above honest:

- **Measure before building.** Several good-looking ideas collapsed when measured (small models
  for classification, similarity scores for ranking). Write down the dead ends so you skip them.
- **Make every silent failure loud.** The expensive bugs are the quiet ones — an issue that built
  but never deployed, a queue that ran dry unnoticed. Turn each into a visible alert.
