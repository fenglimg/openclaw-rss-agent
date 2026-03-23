# X Collector Contract v1

Minimal collector/output contract for integrating X (Twitter) signals into the evolution discovery system.

This contract is designed so that different acquisition backends can be swapped underneath it, including:
- `twitter-cli`
- `twscrape`
- browser automation
- future official API integrations

The downstream system should depend on this contract, not on any specific collector implementation.

---

## Purpose

The collector should not try to solve final judgment.

Its job is to:
1. read watched accounts / watch targets
2. extract recent posts and outbound links
3. normalize canonical objects
4. emit structured signal artifacts for downstream judgment and blending

---

## Required outputs

### 1. `x-author-signals-v1.json`

Per-post or per-signal records.

```json
{
  "version": "v1",
  "items": [
    {
      "platform": "x",
      "author_handle": "example",
      "author_display_name": "Example Person",
      "post_url": "https://x.com/example/status/123",
      "post_id": "123",
      "posted_at": "2026-03-22T00:00:00Z",
      "text_excerpt": "short excerpt",
      "linked_urls": ["https://github.com/owner/repo"],
      "canonical_urls": ["https://github.com/owner/repo"],
      "mention_type": "tool-link",
      "x_signal_role": "author-signal",
      "engagement": {
        "likes": 120,
        "reposts": 15,
        "replies": 8,
        "views": 4000
      },
      "author_signal_weight": 0.8,
      "track_bias": ["applied-ai-evolution"]
    }
  ]
}
```

Primary use:
- editorial context
- author weighting
- raw signal archive

---

### 2. `x-linked-objects-v1.json`

Canonical-object-centric view.

```json
{
  "version": "v1",
  "items": [
    {
      "canonical_url": "https://github.com/owner/repo",
      "object_type": "github-repo",
      "source_posts": [
        "https://x.com/example/status/123",
        "https://x.com/example2/status/456"
      ],
      "authors": ["example", "example2"],
      "mention_types": ["tool-link", "workflow-demo"],
      "track_bias": ["applied-ai-evolution"],
      "x_signal_roles": ["author-signal", "editorial-reference"]
    }
  ]
}
```

Primary use:
- candidate generation
- canonicalization bridge to existing source judgment pipeline

---

### 3. `x-candidate-boosts-v1.json`

A compact downstream-friendly boost signal file.

```json
{
  "version": "v1",
  "items": [
    {
      "canonical_url": "https://github.com/owner/repo",
      "track_bias": ["applied-ai-evolution"],
      "author_count": 2,
      "post_count": 3,
      "repeat_convergence": true,
      "boost_reason": "multiple trusted authors linked the same object within a short time window",
      "boost_strength": 0.7,
      "recommended_effects": [
        "candidate-boost",
        "enrichment-priority"
      ]
    }
  ]
}
```

Primary use:
- candidate generation boost
- enrichment priority boost
- follow queue prioritization

---

### 4. `x-watchlist-summary-v1.md`

Human-readable operational summary.

Should summarize:
- which watched authors produced signals
- which canonical objects repeated
- which objects deserve downstream review
- weak risk/evidence observations if present

Primary use:
- operator review
- fast manual sanity checking

---

## Canonicalization rules

Collectors should canonicalize aggressively before downstream handoff.

### Normalize
- strip tracking params
- resolve common redirect wrappers when feasible
- collapse equivalent GitHub URLs
- preserve original `linked_urls` but emit normalized `canonical_urls`

### Preferred object types
- `github-repo`
- `github-readme-or-blob`
- `official-docs`
- `release-note`
- `blog-post`
- `issue-discussion`
- `landing-page`

---

## Track bias guidance

### `applied-ai-evolution`
Prefer signals about:
- workflow templates
- plugins
- coding CLI usage
- orchestration tools
- practical project demos

### `openclaw-evolution`
Prefer signals about:
- agent behavior
- skills / MCP / tooling
- automation patterns
- reusable assistant/product capabilities

---

## Recommended downstream mapping

### Into candidate generation
Use `x-linked-objects-v1.json` and `x-candidate-boosts-v1.json`.

### Into enrichment priority
Use `repeat_convergence`, `author_count`, and `boost_strength`.

### Into briefs / editorial context
Use `x-author-signals-v1.json` excerpts for short “why now” explanations.

### Into risk/evidence
Use negative posts or contradictory reports as weak evidence only.

---

## Non-goals

This contract should not attempt to encode:
- final `adopt` / `follow` / `deep-dive` judgment
- full social graph analysis
- personal For You replication
- complete X archive semantics

It is intentionally minimal and discovery-focused.
