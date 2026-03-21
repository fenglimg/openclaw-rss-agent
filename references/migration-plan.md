# Migration Plan — From Current RSS Prototype to ClawFeed-based Daily Briefing

## Why this document exists

This document captures:

1. what has already been implemented in the current `/root/openclaw-rss-agent` prototype
2. why the current implementation is no longer the right long-term core
3. why the next mainline should migrate onto `clawfeed` as the base project
4. how future work should proceed by **comparing concrete reference projects**, understanding their strengths/weaknesses, and then **stitching together the best parts** into a stronger system

This is intended to preserve the thinking and validated learnings from the current prototype before large-scale migration / cleanup.

---

## Current judgment

The current prototype proved the direction, but it is still too "toy-like" as a long-term foundation.

### What is working

The prototype already validated that the overall product direction is real:

- OpenClaw-native RSS workflow is feasible
- cron-based digest delivery is feasible
- `isolated agentTurn + announce` is the correct pattern for visible Discord thread delivery
- topic-based triage is useful
- enrichment can be merged back into the scoring path
- Chinese-friendly digest presentation is much better than raw technical output
- Linux.do / community practice content is useful when filtered correctly
- GitHub project radar is needed to make the digest feel complete

### Why the current prototype should not remain the long-term core

Although the prototype is useful, too much of it is currently based on local heuristic patching:

- many ranking decisions are still rule patches layered on top of older rule patches
- output structure improved faster than the underlying architecture
- GitHub radar / novelty / community practical filtering were added incrementally, not from a coherent base design
- story clustering / narrative grouping / topic evolution / multi-source digest assembly are still underpowered
- the overall system still feels like a custom script stack rather than a durable digest platform

So the next phase should **preserve the validated ideas** but **replace the core base**.

---

## What has already been implemented in the prototype

The current prototype already built and validated a non-trivial amount of logic.

### 1. Basic RSS pipeline

Implemented in `/root/openclaw-rss-agent/scripts/`:

- `fetch_feeds.py`
- `dedupe.py`
- `state_io.py`
- `build_digest.py`
- `run_pipeline.py`
- `triage_items.py`

Validated capabilities:

- fetch feed entries from configured RSS sources
- dedupe against prior seen state
- triage items into `send` / `digest` / `drop`
- render digest output
- run as one pipeline entrypoint

### 2. Configurable topic model

Implemented in:

- `/root/openclaw-rss-agent/topic_model.yaml`

Validated concepts:

- `seed_terms`
- `promoted_terms`
- `weak_terms`
- `suppress_terms`
- `cooccurrence_rules`
- scoring thresholds and policy

This means the core theme logic has already moved beyond hardcoded keywords.

### 3. Source / language policy

Validated concepts:

- source-role-based scoring adjustments
- language-based soft adjustments
- per-feed `triage_mode`
- local source keyword boosts / suppressions

### 4. Enrichment flow

Implemented capabilities:

- select small candidate set for enrichment
- validate candidates via local search-layer
- merge enrichment confidence back into final item decisions
- show validation info inside digest output

Validated idea:

- search-layer should be a **secondary validation / discovery layer**, not the primary RSS chain

### 5. Semi-automatic term evolution loop

Implemented scripts:

- `discover_terms.py`
- `validate_terms.py`
- `review_terms.py`
- `promote_terms.py`

Validated idea:

- new terms should **not** auto-promote directly
- use a staged loop: discover → validate → review → promote

### 6. Chinese-friendly digest presentation

Validated improvements:

- switched from technical/raw list output to a more human digest style
- one-line summary / why it matters / suggested action structure is clearly better
- Discord-friendly formatting matters

### 7. Delivery / cron validation

Validated conclusion:

- `sessionTarget=main` + `systemEvent` can execute but may not visibly reply into the channel/thread
- visible Discord results should use:
  - `sessionTarget=isolated`
  - `payload.kind=agentTurn`
  - `delivery.mode=announce`

### 8. Preference shaping already discovered

The target digest should prefer:

- OpenClaw / Claude Code / Codex / Gemini CLI / MCP / skills / workflow automation
- application-layer updates
- new features / changed workflows / workaround / repair / integration / setup / recipe / template / scaffold
- Chinese community practical posts when they are genuinely actionable
- GitHub projects with meaningful scale or momentum

The digest should **avoid** drifting into generic AI news or repetitive low-value hype.

---

## Base-project evaluation result

Three candidates were inspected as potential long-term foundations:

1. `shiquda/rss-agent`
2. `duanyytop/agents-radar`
3. `kevinho/clawfeed`

### `shiquda/rss-agent`

Conclusion:

- useful as a light OpenClaw-native RSS skill example
- too thin to serve as the main foundation
- not suitable as the long-term base for a complete digest system

### `duanyytop/agents-radar`

Conclusion:

- extremely valuable as a reference implementation
- strong in multi-source report building, GitHub tracking, trending, HN, official-web monitoring, digest artifacts, and rollups
- too opinionated / too complete as its own product worldview to cleanly become the sole base for this project
- should be treated as a **capability donor**, not the only mother project

### `kevinho/clawfeed`

Conclusion:

- best current candidate for the base / mother project
- already has:
  - multi-source system
  - source packs
  - storage layer
  - dashboard
  - curation rules
  - digest generation
  - OpenClaw skill integration
- architecturally looks more like a platform than a single-purpose RSS script
- therefore best suited to become the **new main base**

---

## Migration decision

### New base

The next mainline should migrate onto:

- `clawfeed`

### But not as a blind fork

The migration should **not** be “fork clawfeed and stop thinking.”

Instead:

- use `clawfeed` as the structural base
- carry over the validated ideas from the current prototype
- selectively absorb strengths from other reference projects
- explicitly compare each reference before copying behavior

This is a **stitched architecture**, not a wholesale imitation.

---

## Core migration principle

### Stitch concrete advantages from concrete reference systems

Future work should proceed like this:

1. choose one concrete capability to improve
2. inspect 1-2 concrete reference projects / skills that already do it well
3. identify each side’s strengths and weaknesses
4. merge the advantages into the new base
5. avoid copying an entire system just because one module is good

This should be the standing method for all future upgrades.

---

## What the new system should become

The target is no longer “just an RSS tool.”

It should become a:

## complete AI coding / agent tooling daily briefing system

With at least these sections:

1. **Today’s highlights**
2. **Important updates**
3. **Application-layer workflows / new practical uses**
4. **GitHub project radar**
5. **Community practice / repairs / tips**

And the inputs should eventually include more than RSS alone:

- RSS feeds
- GitHub releases / changelogs / trending
- official web updates
- community forums (Linux.do, etc.)
- skill / MCP ecosystem signals
- curated digest/reference sources

---

## What to preserve from the current prototype

The following ideas should be explicitly preserved during migration:

### Preserve these product conclusions

- visible Discord scheduled delivery should use `isolated + announce`
- digest is the default; `send` should be scarce
- application-layer usefulness matters more than generic AI news
- Chinese-friendly reading matters
- Linux.do / Chinese community sources are valuable when filtered for practical signal
- GitHub project radar is necessary to make the briefing feel complete
- search-layer should remain a secondary discovery / validation layer
- term evolution should stay semi-automatic rather than fully auto-promoted

### Preserve these conceptual modules

- topic model / theme system
- source policy / language policy
- enrichment candidate selection and merge-back
- novelty-oriented quality thinking
- practical-vs-generic community filtering
- complete report structure rather than flat top-N list

---

## What should be rebuilt rather than carried over directly

These parts should be rethought on the new base instead of being copied mechanically:

- raw triage heuristics patched over time in the current `triage_items.py`
- temporary score tweaks added only to fix one day’s examples
- ad hoc digest splitting logic that is not fully integrated with delivery
- any logic whose only purpose was to make the current prototype less broken without improving the long-term architecture

In short:

- preserve validated **ideas**
- do not preserve every prototype **implementation detail**

---

## Reference-project-driven stitching roadmap

Below is the intended way to absorb future capabilities.

### 1. Base platform capabilities

Primary base:

- `clawfeed`

Use it for:

- source system
- storage / state foundation
- digest platform structure
- dashboard / source management
- long-term extensibility

### 2. Daily briefing/report assembly

Main references:

- `agents-radar`
- `claude-rss-news-digest`

Borrow from them:

- multi-source report composition
- daily/weekly/monthly rollup concepts
- digest artifact organization
- possible story grouping / narrative grouping concepts

### 3. GitHub project radar

Main references:

- `GitHubTrendingRSS`
- `mcp-github-trending`
- `github-digest`
- `agents-radar`

Target capabilities:

- current star base
- recent star growth
- large-base important repos
- fast-growing new repos
- project classification (template / scaffold / MCP / skill / workflow repo)

### 4. RSS / feed discovery and digest structure

Main references:

- `rss-daily-digest`
- `rss-digest`
- `clawfeed`
- current validated prototype learnings

Target capabilities:

- source discovery
- source packs / curated bundles
- grouped daily briefing instead of flat RSS list

### 5. Skill / MCP ecosystem trend layer

Main references:

- `last30days-weekly`
- ClawHub / awesome-openclaw-skills / skill registry resources

Target capabilities:

- trending skills
- trending MCP servers
- rising ecosystem components
- community interest snapshots

### 6. Community practical signal layer

Main references:

- current prototype learnings from Linux.do
- future comparison of Chinese community implementations / workflows

Target capabilities:

- practical signal extraction
- workaround / setup / integration / repair emphasis
- commodity discussion penalty

---

## Working rule for future comparison

For every reference project or skill studied in the future, evaluate at least these two sides:

### Strengths

- what does it do better than the current system?
- what is structurally reusable?
- what is a real capability vs just nice presentation?

### Weaknesses

- what does it overfit to?
- where is it too opinionated?
- what would break if copied directly?
- what does it still not solve for our target product?

Then:

## stitch the strengths, not the entire identity

That is the key rule.

---

## Immediate next step after this document

After preserving this document, the next structural phase should be:

1. treat current prototype learnings as captured
2. clear the current prototype core from being the long-term mainline
3. begin migration toward a `clawfeed`-based main base
4. reintroduce validated modules one by one
5. continue all future improvement by concrete comparison + stitched advantage transfer

---

## Summary

The prototype has done its job:

- it proved the direction
- it exposed the missing pieces
- it clarified the desired product taste
- it validated critical OpenClaw-native delivery patterns

But it should not remain the final core.

The new mainline should:

- migrate onto `clawfeed`
- preserve current validated product conclusions
- borrow digest/report/radar strengths from concrete reference systems
- compare each reference carefully
- stitch advantages deliberately

This is the intended path from prototype to real product.
