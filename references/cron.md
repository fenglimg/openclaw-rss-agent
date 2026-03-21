# Cron Integration

## Recommended default schedule

Start with 2-4 runs per day, for example:
- 09:00 UTC
- 13:00 UTC
- 18:00 UTC
- 22:00 UTC

Avoid minute-level polling unless there is a strong need.

## Delivery modes

### 1. Main-session reminder style
Use when you want the main session to decide how to respond.

Example systemEvent text:
- "Reminder: run the RSS agent digest check and surface anything high-signal from the last 24 hours."

### 2. Isolated agent run
Use when you want the scheduled task to execute independently and announce results.

Suggested isolated prompt structure:
- run the RSS pipeline
- inspect feed health
- summarize only high-signal items
- if nothing is notable, return a short no-update message

## Practical cron pattern with this repo

Typical task:
1. Run `scripts/run_pipeline.py`
2. Produce Discord-friendly digest text
3. If digest is non-empty and notable, deliver it

Suggested runtime flags:
- `--output-format discord`
- `--write-state`
- suitable `--triage-mode`

## Recommended behavior

- Default to digest mode, not per-item alerts
- If nothing new is found, send a short quiet update or skip delivery
- Keep channel messages compact
- Route high-frequency sources into a digest instead of real-time posting
