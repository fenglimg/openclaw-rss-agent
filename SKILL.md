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

## Workflow

### 1. Load feed configuration
Read `references/feeds.example.yaml` as the format reference.
Use the real feed config file from the workspace if one exists, for example:
- `/root/rss/feeds.yaml`

If the real config file does not exist yet, propose creating it.

### 2. Fetch recent entries
Use `scripts/fetch_feeds.py` to:
- fetch configured RSS/Atom feeds
- normalize fields (`id`, `title`, `link`, `published`, `summary`, `feed_id`)
- emit structured JSON

Prefer fetching only the most recent window needed for the task.

### 3. Dedupe and filter
Use `scripts/dedupe.py` plus workspace state files to:
- skip already-seen entries
- dedupe by `guid`, then `link`, then hash of `title + published`
- filter by:
  - disabled feeds
  - time window
  - include/exclude keywords
  - optional feed tags

### 4. Triage
For small result sets, triage in-model:
- decide which items are worth surfacing
- prefer concrete, high-signal, implementation-relevant posts
- avoid noisy, repetitive, low-information items

Use these rough buckets:
- `send`: worth posting now
- `digest`: worth including in roundup
- `drop`: not worth surfacing

### 5. Summarize
Summarize only selected items.
Default summary shape:
- one-line takeaway
- 2-4 bullets
- original link

If the user asks for a digest, group related items and keep output compact.

### 6. Deliver
If the user asks to send results proactively, use the `message` tool.
Otherwise return the digest in chat.

For Discord:
- do not use markdown tables
- keep links in angle brackets
- prefer bullets and short sections

## Files and state

Recommended workspace layout:
- `/root/rss/feeds.yaml`
- `/root/rss/state.json`
- `/root/rss/output/`

State file should track:
- seen item ids/links/hashes
- last successful run time
- optional per-feed health info

## Safety / quality rules

- Do not spam chat channels with every new RSS item.
- Prefer digest delivery unless the user explicitly wants real-time alerts.
- When feed fetch fails, report feed health separately from content results.
- If article content is missing from RSS, summarize only from the feed entry unless the user asks for full-page fetch.
- Keep summaries grounded in the retrieved entry text and linked page when available.

## When to read references

- Read `references/feeds.example.yaml` when creating or validating feed config.
- Read `references/prompts.md` when you need triage or summary prompt patterns.
- Read `references/architecture.md` when designing cron jobs, delivery routing, or storage layout.

## When to use scripts

- `scripts/fetch_feeds.py`: fetch and normalize entries
- `scripts/dedupe.py`: remove seen/duplicate entries
- `scripts/build_digest.py`: assemble Markdown/plaintext digest
- `scripts/state_io.py`: read/write state safely

## Default operating mode

Unless the user asks otherwise:
- prefer a digest over many single-item posts
- use the last 24 hours as the default time window
- surface only high-signal items
- keep output concise and readable
