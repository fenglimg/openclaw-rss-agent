# Decision Pipeline for the Evolution Discovery System

This document defines the next-stage decision pipeline for the v2 evolution discovery system.

It formalizes a key architectural principle:

> rules should do the first-pass narrowing,
> search-layer should do validation / expansion / source discovery,
> and OpenClaw should do final judgment / synthesis.

This is how the system moves from being a source collector into an actual discovery and evolution engine.

---

## Why this exists

The current system already has major building blocks:

- source packs
- watchlists
- trend-source extraction
- refined trend intelligence
- first output-layer drafts

But if the next step is only “add more sources” or “add more rules,” the system will hit a ceiling.

Rules are necessary, but rules alone cannot answer:
- Is this source actually high quality?
- Is this signal durable or just noisy?
- Is this trend worth adoption or only worth observation?
- Is this source family worth tracking long-term?
- What other repos/authors/digests should be pulled in around this candidate?

So the system needs a structured decision pipeline.

---

## Core principle

### Rules are not the final judge

Rules are best at:
- cheap filtering
- obvious relevance checks
- black/white-listing
- topic/profile constraints
- reducing candidate volume

Rules are **not** best at:
- source quality evaluation
- novelty judgment
- ecosystem interpretation
- adoption judgment
- finding adjacent high-value sources

That work should happen in later layers.

---

## Four-layer pipeline

### Layer 1 — Source Ingest / Collection

Purpose:
- maximize stable recall
- pull data from known and trusted input systems

Typical inputs:
- RSS feeds
- GitHub Trending RSS
- official repos / releases / changelogs
- ClawHub skill listings
- trend pages (`rising`, `top-base`, `weekly`)
- ecosystem watchlists

Responsibilities:
- fetch raw candidates
- normalize fields
- attach source metadata
- preserve enough raw context for later stages

This layer should optimize for:
- coverage
- repeatability
- stability

It should **not** over-think the candidate.

---

### Layer 2 — Rules / Profile Pre-Filter

Purpose:
- do cheap first-pass narrowing before expensive enrichment and agent analysis

Typical signals:
- profile-aware topic matching
- repo-family constraints
- obvious low-signal demotion
- domain exclusion
- language/source-type hard constraints
- allowlist / watchlist boosts
- recency / star thresholds / trend thresholds

Possible outcomes:
- `keep`
- `demote`
- `drop`
- `unsure`

This layer should answer:
- Is this obviously relevant or irrelevant?
- Is this candidate worth spending more compute on?
- Should this candidate be passed to enrichment?

This layer should **not** attempt to fully decide:
- whether the item is strategically important
- whether the source is truly durable
- whether OpenClaw should adopt it

---

### Layer 3 — Search-Layer Enrichment / Validation / Source Expansion

Purpose:
- use search-layer as a second-pass intelligence layer
- validate candidates
- expand context
- discover adjacent sources

This is not raw source ingest replacement.
It is selective enrichment for narrowed candidates.

#### Main roles of search-layer here

##### A. Candidate validation
Search for:
- official docs
- official repos
- release notes
- related issues/discussions
- known authors / organizations
- ecosystem references

Questions answered:
- Is this real and active?
- Is it cited elsewhere?
- Is it a serious project or low-value noise?

##### B. Source expansion
Given a promising candidate, search for:
- related author projects
- related digests / rankings / trackers
- sibling repos / ecosystem families
- official websites / docs / changelogs / community references

Questions answered:
- What else should be tracked around this item?
- Is this part of a larger ecosystem worth ingesting?

##### C. Source quality judgment support
Search for:
- whether a source is original or derivative
- whether it is maintained
- whether other quality references cite it
- whether it has real community adoption signals

Questions answered:
- Should this become a long-term source?
- Is this a discovery-only source or stable-ingest source?

#### Important constraint
Search-layer should only run on:
- `keep`
- `unsure`
- high-signal items
- source-discovery tasks

It should **not** run on the full raw candidate stream.

---

### Layer 4 — OpenClaw Judgment / Synthesis

Purpose:
- turn enriched candidates into product-level decisions

This is where the system stops being a filter and starts being a discovery engine.

OpenClaw (agent judgment) should decide:
- novelty
- strategic relevance
- adoption worthiness
- source worthiness
- how the candidate should be communicated

Typical judgments:
- `adopt`
- `follow`
- `deep-dive`
- `ignore`
- `promote-source`
- `discovery-only`

Questions answered:
- Does this matter for `openclaw-evolution`?
- Does this matter for `applied-ai-evolution`?
- Is this worth integrating, studying, or just observing?
- What is the real lesson or implication?

This layer also produces:
- briefs
- adoption queues
- deep-dive queues
- source candidate queues
- summary narratives / trend interpretations

---

## Pipeline flow

A simplified version:

```text
Layer 1: ingest raw candidates
    ↓
Layer 2: rules pre-filter
    ↓
Layer 3: selective search-layer enrichment
    ↓
Layer 4: OpenClaw judgment + synthesis
    ↓
outputs / queues / source promotion decisions
```

---

## Candidate state model

A candidate should be able to move through explicit states.

Suggested states:
- `raw`
- `prefilter_keep`
- `prefilter_demote`
- `prefilter_drop`
- `prefilter_unsure`
- `enriched`
- `judged_adopt`
- `judged_follow`
- `judged_deep_dive`
- `judged_ignore`
- `source_candidate`
- `source_promoted`

This allows the system to treat “content candidate” and “source candidate” as related but distinct concepts.

---

## Two kinds of outputs

The system should output not only content summaries, but also source decisions.

### A. Content outputs
Examples:
- evolution brief
- adoption queue
- deep-dive queue
- applied brief

### B. Source outputs
Examples:
- source candidate queue
- promoted source list
- watchlist expansion suggestions
- source taxonomy updates

This matters because some items are valuable mostly as:
- new tracking targets
- new weekly references
- new ranking pages
- new author ecosystems

not just as digest items.

---

## How this applies to `openclaw-evolution`

### What the pipeline should optimize for
Not “what is merely hot,” but:
- what skills/patterns are rising repeatedly
- what behaviors users clearly value
- what reusable surfaces OpenClaw could absorb
- what ecosystem changes imply durable product pressure

### Likely judgments
Examples:
- `self-improving-agent` → possible `adopt`
- `Agent Browser` → possible `adopt`
- `Summarize` → possible `adopt`
- `Polymarket` → likely `deep-dive` or `ignore` unless broader lesson appears
- `Baidu Search` → possible `deep-dive` for regional demand signal

### Source promotion examples
- `clawhubtrends-rising` → promote as trend-intelligence source
- `topclawhubskills` → promote as top-base source
- `last30days-weekly` → likely promote as weekly intelligence source

---

## How this applies to `applied-ai-evolution`

### What the pipeline should optimize for
Not “all trending AI repos,” but:
- practical coding-agent workflows
- reusable frameworks / orchestrators / toolchains
- high-signal project radar items
- author ecosystems worth following
- builder-facing weekly briefings worth learning from

### Likely judgments
Examples:
- a Claude Code workflow framework → `follow` or `adopt`
- a generic infra project with weak applied relevance → `ignore`
- a strong builder digest site → `promote-source`
- a promising repo family → `source_candidate` + `follow`

---

## Recommended implementation strategy

### Phase 1 — document the pipeline
This document.

### Phase 2 — minimal enrichment layer
Create a small enrichment script, for example:
- `scripts-v2/enrich_candidates.py`

It should:
- take high-signal candidates from rules output
- run targeted search-layer queries
- attach validation / expansion metadata
- output enriched candidates for judgment

### Phase 3 — judgment integration
Create a minimal judgment pass that uses:
- raw candidate
- rule score/state
- trend signal
- search-layer enrichment

to produce:
- adopt / follow / deep-dive / ignore
- source_candidate / source_promoted hints

### Phase 4 — output refinement
Use enriched judgments to improve:
- briefs
- adoption queues
- deep-dive queues
- source candidate queues

---

## Design constraints

### 1. Do not let search-layer replace ingest
Source ingest must remain the stable recall layer.

### 2. Do not let rules decide everything
Rules should narrow, not conclude.

### 3. Do not let the agent judge raw full-volume streams
The agent should operate on narrowed, enriched candidates.

### 4. Treat source discovery as a first-class outcome
A candidate can reveal a better source, and that can be more valuable than the candidate itself.

### 5. Keep source quality separate from popularity
A popular item is not always a high-quality source.
A niche source can still be strategically valuable.

---

## Immediate next step recommendation

The most sensible next concrete step after this document is:

### Build a minimal `enrich_candidates.py`
for one track first, ideally `openclaw-evolution`.

Input:
- prefiltered high-signal items

Process:
- run search-layer for validation / source expansion

Output:
- enriched candidate JSON with fields like:
  - `validation_sources`
  - `related_projects`
  - `related_authors`
  - `source_quality_notes`
  - `source_candidate_urls`
  - `suggested_judgment`

That would be the first real implementation of this pipeline.

---

## Final principle

This project should evolve from:
- source collector
- rule-based triage
- digest generator

into:
- source-aware discovery system
- selective enrichment engine
- judgment-driven evolution intelligence pipeline

That is the real next stage of the system.
