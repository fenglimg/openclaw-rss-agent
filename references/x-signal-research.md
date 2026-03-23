# X Signal Research v0

Research notes for adding X (Twitter) as an input layer to the evolution discovery system.

## Position in the system

X should **not** be treated as `stable-ingest`.

Recommended roles:
- `author-signal`
- `discovery-index`
- `editorial-reference`
- sometimes `risk/evidence`

Why:
- signal can appear on X earlier than canonical sources
- many practical workflow/tooling discoveries spread first via builders on X
- but X signal is noisy, uneven, and often weak as standalone evidence

So X should help with:
- discovery
- trend surfacing
- author tracking
- early attention signals

Not with:
- final canonical validation by itself
- stable low-noise ingest

---

## High-value reference projects

### 1. `jackwener/twitter-cli` / `public-clis/twitter-cli`

Why it matters:
- terminal-first X/Twitter interface
- supports `for-you` / `following` / bookmarks / lists / search
- already includes filtering and structured output ideas
- most directly relevant to a minimal X source layer

Key takeaways:
- timeline access and filtering can be unified behind one CLI abstraction
- feed objects should be structured for downstream ranking / filtering
- optional scoring filter is a useful pattern for first-pass narrowing

Recommended role in our reference map:
- strongest practical reference for a minimal X ingest layer

---

### 2. `vladkens/twscrape`

Why it matters:
- realistic modern scraping/GraphQL reference
- async search/timeline support
- account rotation / rate limit smoothing

Key takeaways:
- if we ever need a deeper X ingestion path, this is closer to a realistic backend reference than older projects
- useful for understanding current X object shapes and scraping constraints

Recommended role:
- backend / acquisition-layer reference

---

### 3. `StanfordHCI/FeedMonitor`

Why it matters:
- directly studies intercepting / logging / modifying social feeds in real time
- useful blueprint for rerank / filter / transform experiments

Key takeaways:
- the interesting problem is not only scraping the feed
- the interesting problem is logging the raw feed and applying transformation layers:
  - rerank
  - filter
  - summarize
  - experiment

Recommended role:
- strongest blueprint for feed filtering / reranking architecture

---

### 4. `laiso/xpaper`

Why it matters:
- curates timeline content into a cleaner digest/newsletter format
- much closer to our output-layer goals than a generic scraper

Key takeaways:
- timeline → curate → summarize → digest is a directly relevant pattern
- X signal becomes much more usable once transformed into digestable artifacts

Recommended role:
- digest / transformation-layer reference

---

### 5. `twitter/the-algorithm`

Why it matters:
- official open-sourced recommendation algorithm lineage
- not a plug-and-play implementation for our system, but strategically important

Key takeaways:
- feed ranking is a multi-stage problem:
  - candidate generation
  - heuristics / filtering
  - scoring / ranking
  - blending / policy decisions
- this supports our judgment architecture intuition: signal strength alone is not enough; ranking needs structure

Recommended role:
- conceptual ranking reference

---

### 6. `igorbrigadir/awesome-twitter-algo`

Why it matters:
- annotated learning index around the Twitter recommendation algorithm

Key takeaways:
- useful as a reading map for recommendation / recsys lessons
- helps separate algorithm ideas from implementation details

Recommended role:
- learning/reference index

---

## Supporting references

### `twintproject/twint`
- huge historical star signal
- important as a legacy baseline
- less suitable as the primary modern implementation reference

### `amitlevy/x-content-filter-openrouter`
### `ricklamers/x-ai-content-filter-groq`
- useful examples of LLM-based X content filtering
- smaller projects, but directly relevant to semantic filtering patterns

### `mhwdvs/twitter-monitor`
### `ionic-bond/twitter-monitor`
- monitoring / alerting / watchlist style references
- useful for account-watch and event-routing ideas

---

## Architectural lessons for our system

### Lesson 1 — Separate access from judgment
Do not mix:
- timeline access
- filtering
- summarization
- source judgment

Instead think in layers:
1. access / acquisition
2. normalization
3. first-pass filtering
4. semantic calibration
5. output synthesis

---

### Lesson 2 — X should bias discovery, not final truth
An X post mentioning a repo/tool can increase:
- discovery priority
- author-signal weight
- trend attention

But should not by itself establish:
- canonical adoption worthiness
- source credibility
- long-term tracking value

X needs downstream canonical confirmation via:
- GitHub repo
- official docs
- release notes
- credible editorial references

---

### Lesson 3 — watch authors, not just keywords
For our use case, account-level tracking is likely more valuable than pure keyword scraping.

Promising signals:
- repeated mentions by trusted builders
- repeated links to the same repo/doc/tool
- cross-account convergence around the same object
- linked artifacts that can be normalized into canonical sources

This supports an `author-signal` model better than raw keyword firehose ingestion.

---

### Lesson 4 — feed filtering is a reranking problem
The Twitter algorithm reference and FeedMonitor both reinforce that feed quality is not only about collection.

The valuable problem is:
- which candidates get into the pool
- how they are reranked
- what gets hidden / deferred / promoted
- what becomes digest material

This maps closely onto our existing:
- source judgment
- calibration rules
- adopt / follow / deep-dive split

---

## Proposed minimal X source object

```json
{
  "platform": "x",
  "author": "handle",
  "post_url": "https://x.com/...",
  "post_id": "...",
  "posted_at": "ISO-8601 or empty",
  "linked_urls": ["..."],
  "canonical_urls": ["..."],
  "mention_type": "tool-link|workflow-demo|editorial-opinion|release-signal|trend-signal",
  "engagement": {
    "likes": null,
    "reposts": null,
    "replies": null,
    "views": null
  },
  "author_signal_weight": 0.0,
  "x_signal_role": "author-signal"
}
```

---

## Recommended next implementation step

Not full ingestion yet.

First do:
- `x-source-spec-v0`
- `author-watchlist` concept
- `x-signal` taxonomy entries

Then later consider:
- a minimal collector using an external tool / CLI
- normalization into canonical URLs
- source-role assignment (`author-signal`, `editorial-reference`, `risk/evidence`)

---

## Current judgment

X is worth adding.

But for this system, the right framing is:
- **X as early signal and author-discovery layer**

not:
- **X as stable truth layer**
