# Topic Model

This file defines the evolving topic system for the RSS agent.

## Goals

- separate stable seed ideas from observed promoted terms
- reduce noisy one-word keyword matching
- support future promotion/demotion workflows
- make source role and language explicit inputs to scoring

## Sections

### `topic_model.seed_terms`
Initial hand-chosen seed concepts.
Treat these as starting assumptions, not immutable truth.

### `topic_model.promoted_terms`
Terms promoted from observation.
These should come from repeated appearances in high-signal kept items.

### `topic_model.weak_terms`
Broad terms that may be relevant but are too generic to carry much score on their own.

### `topic_model.suppress_terms`
Terms strongly associated with off-topic or low-value content for this digest.

### `topic_model.cooccurrence_rules`
Phrase-like rules expressed as multiple tokens that are more reliable together than alone.

### `source_policy`
Source-role and source-specific weighting.
Use this to favor official releases/changelogs and down-weight noisy aggregators.

### `language_policy`
Language is a small adjustment, not the main decision factor.
Use it to reflect where certain types of signal tend to appear:
- English: releases, changelogs, protocol updates
- Chinese: deployment tips, workarounds, usage tricks

### `scoring_policy`
Global multipliers and thresholds for send/digest/drop behavior.

### `update_policy`
Guidance for weekly review loops and controlled promotion/demotion.

## Recommended maintenance process

1. Collect high-signal kept items for a week.
2. Extract recurring candidate terms and co-occurring phrases.
3. Check whether they appear across multiple sources.
4. Promote only a few per review cycle.
5. Demote or suppress terms that repeatedly introduce noise.
