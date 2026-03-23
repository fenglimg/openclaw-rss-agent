# X Source Spec v0

Minimal source specification for integrating X (Twitter) into the evolution discovery system.

## Purpose

This spec defines how X-derived signals should enter the system without being treated as a stable primary source.

X should function as:
- `author-signal`
- `discovery-index`
- `editorial-reference`
- sometimes `risk/evidence`

It should not function as:
- `stable-ingest`
- standalone canonical validation

---

## Why X belongs in the system

X often surfaces useful objects earlier than:
- RSS feeds
- official changelogs
- digest posts
- GitHub trend surfaces

This is especially true for:
- workflow demos
- plugin/tooling reveals
- builder recommendations
- “what I am using lately” posts
- early project attention bursts

So X is valuable as an early discovery and attention layer.

---

## Core principle

The system should not treat a post on X as the main durable object.

The durable object should usually be one of:
- GitHub repo
- docs page
- release note
- blog post
- landing page
- issue / discussion

The X post is metadata about attention, endorsement, criticism, or framing.

---

## Minimal X source object

```json
{
  "platform": "x",
  "author_handle": "example",
  "author_display_name": "Example Person",
  "post_url": "https://x.com/example/status/123",
  "post_id": "123",
  "posted_at": "2026-03-22T00:00:00Z",
  "text_excerpt": "short excerpt",
  "linked_urls": [
    "https://github.com/owner/repo",
    "https://docs.example.com/page"
  ],
  "canonical_urls": [
    "https://github.com/owner/repo"
  ],
  "mention_type": "tool-link",
  "x_signal_role": "author-signal",
  "engagement": {
    "likes": null,
    "reposts": null,
    "replies": null,
    "views": null
  },
  "author_signal_weight": 0.0,
  "notes": "optional parser or collector notes"
}
```

---

## `mention_type` taxonomy

Recommended first-pass values:
- `tool-link`
- `workflow-demo`
- `editorial-opinion`
- `release-signal`
- `trend-signal`
- `risk-report`
- `author-recommendation`
- `comparison-thread`

These should not directly decide final judgment, but can affect discovery and prioritization.

---

## `x_signal_role` taxonomy

Recommended first-pass values:
- `author-signal`
- `editorial-reference`
- `risk/evidence`
- `discovery-index`

---

## Canonicalization rules

After collecting an X object:
1. extract outbound URLs
2. normalize redirects / tracking params
3. identify canonical targets
4. attach the X object as signal metadata to canonical targets

Examples:
- X post links to `github.com/jarrodwatts/claude-hud`
- the durable object becomes the GitHub repo
- the X object becomes attention / editorial / author signal metadata

If no durable outbound object exists, the post can remain only as:
- `editorial-reference`
- `risk/evidence`

---

## Where X should influence the system

### 1. Candidate generation
Promote objects into the candidate pool earlier when repeated X signals point to them.

### 2. Enrichment priority
Prioritize enrichment when:
- multiple trusted authors mention the same canonical object
- the object appears across multiple X posts within a short window

### 3. Brief context
Use X posts as supporting explanation for:
- why a project is suddenly attention-worthy
- what practitioners find useful about it

### 4. Risk signals
Use X as a weak but useful source for:
- complaints
- breakage reports
- trust concerns
- hype-vs-reality corrections

---

## What X should NOT do

X should not directly:
- promote an object to `adopt`
- replace source judgment
- replace official/canonical validation
- overrule strong contradictory evidence from better sources

---

## Intended first consumers

### `applied-ai-evolution`
Primary beneficiary.

Why:
- workflow/tooling discoveries often spread first through builders on X
- demos and real usage patterns are often more visible there than in docs

### `openclaw-evolution`
Secondary beneficiary.

Why:
- less important than canonical OpenClaw ecosystem sources
- still useful for emerging behavior/tooling attention

---

## Recommended next step

Implement an `x-watchlist` around trusted authors instead of broad keyword firehose ingestion.
