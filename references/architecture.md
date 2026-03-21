# RSS Agent Architecture

## Recommended layout

- config: `/root/rss/feeds.yaml`
- state: `/root/rss/state.json`
- output: `/root/rss/output/`

## Delivery modes

### Digest mode
Best default for Discord channels.
Use scheduled runs and produce a compact summary.

### Alert mode
Use only for high-priority items or explicit user request.

## Cron recommendation

Start with 2-4 runs per day.
Avoid minute-level polling unless specifically needed.

## Dedupe keys

Priority:
1. guid/id
2. link
3. hash(title + published)

## Feed health

Track:
- last successful fetch
- last failure
- error count
