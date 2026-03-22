# Search-layer Enrichment v1

## Goal

Add a lightweight validation stage after deterministic triage, using search-layer only for a small subset of candidate items.

This stage should improve confidence for likely high-value items without turning every RSS run into a web-search workflow.

## Scope for v1

Only validate items that are already close to `send` or top-end `digest`.
Do not run search-layer for every fetched item.

## Candidate selection

Select items for enrichment when any of these are true:
- triage decision is `send`
- triage score is within a configurable margin below `send`
- item comes from a noisy source but has a high score
- item contains a potentially novel term or phrase worth verification

## Validation questions

For each selected item, search-layer should try to answer:
1. Is this topic appearing in multiple credible sources?
2. Is there an official source, changelog, release note, or engineering post related to it?
3. Is it a one-off community mention or a broader signal?

## Suggested output shape

```json
{
  "validated": true,
  "crossSourceCount": 3,
  "officialHit": true,
  "confidenceDelta": 0.8,
  "relatedSources": [
    {"title": "...", "url": "...", "kind": "official_release"},
    {"title": "...", "url": "...", "kind": "engineering_blog"}
  ],
  "reason": "Confirmed by official changelog and a second engineering source"
}
```

## Scoring effect

Suggested first-pass effect:
- official hit: +0.6 to +1.0
- multiple credible sources: +0.3 to +0.8
- only weak/low-quality corroboration: +0.0
- no corroboration: optionally -0.2 or no change

## Operational rules

- Cap validated candidates per run (for example 1-3 items)
- Prefer official and engineering sources over generic media
- Keep search-layer enrichment optional and configurable
- If search-layer is unavailable, fall back to deterministic triage with no failure

## Recommended future fields in topic model

Possible future config:

```yaml
enrichment_policy:
  enabled: true
  max_candidates_per_run: 2
  validate_send_candidates: true
  validate_high_digest_candidates: true
  send_margin: 0.7
  noisy_source_roles:
    - aggregator
    - media
```
