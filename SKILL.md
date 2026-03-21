---
name: rss-agent
description: >
  Agentic RSS workflow for OpenClaw. Use when the user wants to fetch RSS/Atom feeds,
  monitor updates, build digests, filter items by keywords or relevance, summarize
  articles, check whether feeds are healthy, or deliver curated RSS results to Discord
  or other chat channels. Best for RSS triage, daily digests, topic-focused monitoring,
  and lightweight self-hosted feed automation.
---

# RSS Agent

Use this skill for RSS/Atom feed workflows:
- read and check feeds
- monitor feeds for new items
- filter by topic, keyword, or time window
- create daily or ad-hoc digests
- summarize interesting entries
- route curated results to chat channels

## Default workflow

For most tasks, use the pipeline runner:

```bash
python3 {baseDir}/scripts/run_pipeline.py \
  --config /root/rss/feeds.yaml \
  --state /root/rss/state.json \
  --window-hours 24 \
  --limit-per-feed 10 \
  --triage-mode general-tech \
  --digest-title "📡 RSS Digest"
```

This runner chains:
1. `fetch_feeds.py`
2. `dedupe.py`
3. `triage_items.py`
4. `build_digest.py`

Use lower-level scripts directly only for debugging, testing, or custom routing.

## Triage modes

Supported modes:
- `general-tech`: broader technical roundup mode for devtools, OSS, GitHub, and general engineering news
- `agentic`: narrower mode for OpenClaw, agents, workflows, automation, coding agents, and related tooling

The pipeline accepts a default mode via `--triage-mode`.
Each feed may override that default with `triage_mode` in the feed config.

## Feed configuration

Recommended workspace layout:
- `/root/rss/feeds.yaml`
- `/root/rss/state.json`
- `/root/rss/output/`

Use `references/feeds.example.yaml` as the format reference.

Per-feed fields:
- `id`
- `name`
- `url`
- `enabled`
- `tags`
- `triage_mode`
- `include`
- `exclude`
- `boost_keywords`
- `suppress_keywords`
- `priority_topics`

Notes:
- `boost_keywords` and `priority_topics` only score against real fetched content, not against config text itself
- feed-local `triage_mode` overrides the pipeline default for that feed
- use `include` / `exclude` for hard filtering, and `boost_keywords` / `priority_topics` for softer ranking

## Task recipes

### 1. Build a digest in chat
Run `run_pipeline.py` and return the `digest` text.
Default behavior:
- last 24 hours
- compact digest
- no proactive send unless requested

### 2. Check feed health
Use `fetch_feeds.py` when the user asks whether feeds are working.
Report:
- which feeds succeeded
- which feeds failed
- status code / error
- item count fetched

### 3. Debug filtering or triage
Use scripts separately when debugging:
- `fetch_feeds.py`
- `dedupe.py`
- `triage_items.py`

Inspect:
- include/exclude rules
- time windows
- dedupe behavior
- mode differences
- triage debug fields (`base_hits`, `boost_hits`, `priority_hits`, `suppress_hits`)

### 4. Proactive delivery
If the user explicitly asks to send results to Discord or another channel:
- run `run_pipeline.py`
- inspect the `digest`
- use the `message` tool to deliver it

For Discord:
- do not use markdown tables
- keep links in angle brackets
- prefer bullets and short sections

## State and dedupe

State file tracks:
- seen item ids/links/hashes
- last successful run time
- per-feed health snapshots

Dedupe priority:
1. `guid` / `id`
2. `link`
3. hash of `title + published`

## Quality rules

- Do not spam channels with every new RSS item.
- Prefer digest delivery unless the user explicitly wants real-time alerts.
- When feed fetch fails, report feed health separately from content results.
- If article content is missing from RSS, summarize only from the feed entry unless the user asks for full-page fetch.
- Keep summaries grounded in retrieved text.
- Treat `send` as scarce and `digest` as the normal default.

## When to read references

- `references/feeds.example.yaml` — when creating or validating feed config
- `references/prompts.md` — when adding AI triage or summary prompts
- `references/architecture.md` — when designing storage and routing
- `references/usage.md` — when you need command examples and OpenClaw integration patterns
- `references/cron.md` — when the user wants reminders, scheduled digests, or channel delivery automation

## When to use scripts

- `scripts/run_pipeline.py`: default entry point
- `scripts/fetch_feeds.py`: fetch and normalize entries
- `scripts/dedupe.py`: remove seen/duplicate entries
- `scripts/triage_items.py`: assign `send` / `digest` / `drop`
- `scripts/build_digest.py`: assemble digest text
- `scripts/state_io.py`: read/write state safely

## Default operating mode

Unless the user asks otherwise:
- prefer a digest over many single-item posts
- use the last 24 hours as the default time window
- use `general-tech` as the pipeline default
- let feed-local `triage_mode` override when configured
- keep output concise and readable
