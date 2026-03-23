# X Watchlist v0

Minimal watchlist design for using X (Twitter) as an author-signal layer in the evolution discovery system.

## Goal

Track a small set of high-signal X accounts and extract linked canonical objects that may deserve:
- candidate creation
- follow priority
- enrichment priority
- editorial context

This is not meant to be a full X firehose collector.

---

## Why watchlists first

Broad X ingestion creates too much noise.

A curated watchlist gives better signal quality for:
- workflow discovery
- plugin/tooling discovery
- emerging builder patterns
- repeated attention to the same canonical object

---

## What to watch

Recommended account classes:
- builder / maker accounts
- AI coding workflow practitioners
- Claude Code / Codex / Gemini CLI power users
- researchers who consistently link useful repos/docs
- ecosystem curators / demo-heavy accounts

---

## Watch target object

```json
{
  "handle": "example_handle",
  "display_name": "Example Person",
  "priority": "high",
  "track_bias": ["applied-ai-evolution"],
  "topics": ["claude-code", "codex", "workflow", "plugins"],
  "notes": "why this account is worth tracking"
}
```

---

## Collector output expectations

For each watched account, the collector should ideally produce:
- recent posts
- outbound URLs
- normalized canonical URLs
- mention type
- optional engagement fields

Suggested output files:
- `test-output/x-author-signals-v1.json`
- `test-output/x-linked-objects-v1.json`
- `outputs/x-watchlist-summary-v1.md`

---

## First-pass scoring ideas

### Author weight
Base weight should depend on:
- past usefulness of surfaced objects
- consistency of linking real canonical objects
- domain relevance to the target profile

### Mention weight
Increase weight for posts that:
- link GitHub/docs/release notes directly
- explain why something matters
- demonstrate actual workflow use

### Convergence boost
Increase candidate priority when:
- multiple watched authors mention the same canonical object
- mentions cluster within a short time window

---

## Recommended downstream effects

### Candidate boost
If an object is surfaced by multiple trusted authors, increase candidate priority.

### Enrichment trigger
If a watched author links a likely high-value repo/doc, prioritize search-layer enrichment.

### Editorial context
Allow the post excerpt to supply short “why now / why this matters” context in briefs.

### Risk/evidence
Negative reports from trusted authors can attach weak risk metadata to a candidate.

---

## Suggested first implementation scope

Keep v0 deliberately small:
- 10–30 watched accounts
- 1–3 profile biases per account
- recent posts only
- outbound-link-first extraction
- canonicalization before downstream use

---

## Integration with current system

### Applied track
Use X watchlist primarily to improve:
- candidate generation
- follow/adopt boundary calibration
- editorial explanation in briefs

### OpenClaw track
Use X watchlist secondarily to improve:
- detection of emerging behavior/tooling attention
- weak corroboration for follow candidates

---

## Non-goals for v0

Do not attempt:
- full personal timeline replication
- For You recommendation reproduction
- full-blown social graph modeling
- keyword firehose collection across all X

The goal is a small, high-signal author layer.
