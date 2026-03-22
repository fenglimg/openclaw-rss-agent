# Usage Patterns

## Basic digest run

```bash
python3 scripts/run_pipeline.py \
  --config /root/rss/feeds.yaml \
  --state /root/rss/state.json \
  --window-hours 24 \
  --limit-per-feed 10
```

## Explicit triage mode

```bash
python3 scripts/run_pipeline.py \
  --config /root/rss/feeds.yaml \
  --state /root/rss/state.json \
  --triage-mode agentic
```

## Force a global triage mode

Use this when you want all feeds evaluated under one mode, ignoring per-feed `triage_mode`.

```bash
python3 scripts/run_pipeline.py \
  --config /root/rss/feeds.yaml \
  --state /root/rss/state.json \
  --triage-mode agentic \
  --ignore-feed-mode
```

## Discord-friendly output

```bash
python3 scripts/run_pipeline.py \
  --config /root/rss/feeds.yaml \
  --state /root/rss/state.json \
  --output-format discord
```

## Wider time window

```bash
python3 scripts/run_pipeline.py \
  --config /root/rss/feeds.yaml \
  --state /root/rss/state.json \
  --window-hours 168 \
  --limit-per-feed 20
```

## Persist seen items

```bash
python3 scripts/run_pipeline.py \
  --config /root/rss/feeds.yaml \
  --state /root/rss/state.json \
  --write-state
```

## Save JSON for further routing

```bash
python3 scripts/run_pipeline.py \
  --config /root/rss/feeds.yaml \
  --state /root/rss/state.json \
  --output-json /root/rss/output/pipeline.json
```

## Debug fetch only

```bash
python3 scripts/fetch_feeds.py \
  --config /root/rss/feeds.yaml \
  --limit-per-feed 10
```

## Debug dedupe only

```bash
python3 scripts/dedupe.py \
  --items /root/rss/output/fetched.json \
  --state /root/rss/state.json \
  --window-hours 24
```

## Debug triage only

```bash
python3 scripts/triage_items.py \
  --input /root/rss/output/deduped.json \
  --mode general-tech
```

## Debug triage with forced mode

```bash
python3 scripts/triage_items.py \
  --input /root/rss/output/deduped.json \
  --mode agentic \
  --ignore-feed-mode
```

## Config notes

Per-feed config can set:
- `triage_mode`
- `boost_keywords`
- `suppress_keywords`
- `priority_topics`

Use `include` / `exclude` for stronger filtering.
Use `boost_keywords` / `priority_topics` for softer ranking.
Use `--ignore-feed-mode` when you want pipeline-level mode to override all feeds.

## OpenClaw usage pattern

Typical agent flow:
1. Run `scripts/run_pipeline.py`
2. Inspect JSON when needed
3. Deliver the `digest` text in chat or via `message.send`
