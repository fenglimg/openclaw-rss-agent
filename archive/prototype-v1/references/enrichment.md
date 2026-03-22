# Search-layer Enrichment Strategy

## Purpose

Use search-layer as a selective enrichment layer, not as the primary fetch mechanism.
RSS remains the stable monitoring layer. Search-layer adds discovery and validation.

## Trigger cases

### 1. New-term discovery
Trigger when:
- a kept item contains an unfamiliar but repeated phrase
- a term appears in multiple high-signal items
- a community source references a potentially important new concept

Use search-layer to answer:
- is this term actually relevant to OpenClaw / coding agents / MCP / skill ecosystems?
- is it showing up across multiple credible sources?
- should it become a promoted term candidate?

### 2. High-value item validation
Trigger for:
- likely `send` items
- high-scoring `digest` items from noisy sources

Use search-layer to answer:
- is this topic confirmed by multiple sources?
- is there an official release, changelog, or engineering post behind it?
- is it a one-off community discussion or a broader signal?

### 3. Periodic source discovery
Run on a slower cadence (for example weekly) to discover:
- new blogs
- release feeds
- changelog pages
- high-signal authors
- skill registries or curated lists worth tracking

## Design principles

- Do not search every RSS item.
- Only enrich the minority of items that are high-value, ambiguous, or novel.
- Use search results to adjust confidence, not to replace RSS history.
- Favor official or engineering sources when validating an item.

## Future outputs

A future enrichment pass may emit:
- `cross_source_bonus`
- `validated_by_official_source`
- `candidate_promoted_terms`
- `candidate_new_sources`
