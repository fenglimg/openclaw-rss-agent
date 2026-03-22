# Delivery Integration

## Goal

Turn RSS pipeline output into a compact message suitable for OpenClaw chat delivery or scheduled posting.

## Recommended delivery model

### In-chat / on-demand
- Run `scripts/run_pipeline.py`
- Read the digest text
- Return it directly in the current conversation

### Proactive / scheduled
- Run `scripts/run_pipeline.py`
- If the digest is empty or says there is nothing notable, optionally skip delivery
- Otherwise send the digest with OpenClaw `message.send`

## Suggested channel behavior

### Discord
- prefer digest format over per-item spam
- keep links wrapped in angle brackets
- no markdown tables
- group items compactly

## Pipeline output formats

`run_pipeline.py` supports:
- `--output-format json` — default, best for machine chaining
- `--output-format text` — plain digest text for terminals or simple piping
- `--output-format discord` — digest text intended for Discord delivery

## Practical pattern for OpenClaw

1. Run pipeline in JSON mode when the agent needs structured inspection
2. Use the `digest` field for final delivery
3. Or run in `--output-format discord` if you only need the ready-to-send text

## Delivery policy

- treat `send` as rare
- treat digest delivery as the norm
- do not proactively send low-signal/no-update outputs unless the user wants heartbeat-style status messages
