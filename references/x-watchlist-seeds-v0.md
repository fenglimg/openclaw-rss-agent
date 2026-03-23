# X Watchlist Seeds v0

First seed template for building an `x-watchlist` author-signal layer.

This file intentionally does **not** claim a finalized set of real handles yet.
It defines the structure and selection logic so we can add actual accounts carefully.

---

## Selection principles

Prioritize accounts that consistently do one or more of the following:
- share real repo/doc/release/demo links
- explain practical workflow/tooling value
- surface new Claude Code / Codex / Gemini CLI / AI tooling patterns early
- show actual usage, not just hype reposts
- repeatedly point to canonical objects worth downstream validation

Avoid accounts dominated by:
- generic AI hype
- vague hot takes without links
- engagement farming
- copy-trading / news parroting

---

## Seed object shape

```json
{
  "handle": "example_handle",
  "display_name": "Example Person",
  "priority": "high",
  "track_bias": ["applied-ai-evolution"],
  "topics": ["claude-code", "codex", "workflow", "plugins"],
  "selection_reason": "Frequently links real workflow/tooling artifacts with useful commentary.",
  "expected_signal_types": ["tool-link", "workflow-demo", "author-recommendation"]
}
```

---

## Candidate classes

### Class A — practical AI coding workflow builders
Target characteristics:
- regularly post about Claude Code / Codex / Gemini CLI usage
- link repos, templates, prompts, plugins, docs
- show real workflows instead of general opinions

Preferred track bias:
- `applied-ai-evolution`

Expected signal types:
- `tool-link`
- `workflow-demo`
- `author-recommendation`

---

### Class B — ecosystem curators / collectors
Target characteristics:
- maintain curated lists, directories, plugin collections, awesome lists
- surface many canonical links
- help identify repeated ecosystem attention

Preferred track bias:
- `applied-ai-evolution`
- sometimes `openclaw-evolution`

Expected signal types:
- `editorial-opinion`
- `trend-signal`
- `tool-link`

---

### Class C — agent / tooling researchers
Target characteristics:
- analyze agent workflows, coding tools, MCP/skills/tooling ecosystems
- post comparisons, evaluations, recommendation threads
- often useful for `editorial-reference`

Preferred track bias:
- both tracks

Expected signal types:
- `comparison-thread`
- `editorial-opinion`
- `trend-signal`

---

### Class D — OpenClaw-adjacent builders
Target characteristics:
- discuss skills, MCP, agent behavior, automation patterns
- link to repos, skill packs, experiments, ecosystem references

Preferred track bias:
- `openclaw-evolution`

Expected signal types:
- `tool-link`
- `release-signal`
- `author-recommendation`

---

## Initial seed placeholders

These are placeholders for the first real seed set. They should be replaced only after manual review.

```json
[
  {
    "handle": "seed_builder_1",
    "display_name": "Seed Builder 1",
    "priority": "high",
    "track_bias": ["applied-ai-evolution"],
    "topics": ["claude-code", "workflow", "plugins"],
    "selection_reason": "Placeholder for a high-signal workflow/tooling builder.",
    "expected_signal_types": ["tool-link", "workflow-demo"]
  },
  {
    "handle": "seed_curator_1",
    "display_name": "Seed Curator 1",
    "priority": "medium",
    "track_bias": ["applied-ai-evolution", "openclaw-evolution"],
    "topics": ["agent-tools", "directories", "awesome-lists"],
    "selection_reason": "Placeholder for a curator that repeatedly links useful canonical objects.",
    "expected_signal_types": ["tool-link", "trend-signal"]
  },
  {
    "handle": "seed_openclaw_1",
    "display_name": "Seed OpenClaw 1",
    "priority": "medium",
    "track_bias": ["openclaw-evolution"],
    "topics": ["skills", "mcp", "agent-behavior"],
    "selection_reason": "Placeholder for an OpenClaw-adjacent builder or researcher.",
    "expected_signal_types": ["tool-link", "release-signal", "author-recommendation"]
  }
]
```

---

## How to use this file

### Step 1
Replace placeholders with manually reviewed real handles.

### Step 2
Start with a small set (10–20 accounts), not a large corpus.

### Step 3
For each real account, record:
- why it is trusted
- what kinds of canonical objects it tends to surface
- which track it benefits more

### Step 4
Only after that, build a minimal collector.

---

## Downstream expectations

A future collector should use these watch seeds to produce:
- `x-author-signals-v1.json`
- `x-linked-objects-v1.json`
- `x-candidate-boosts-v1.json`

Those outputs should then feed:
- candidate generation
- enrichment priority
- editorial context
- weak risk/evidence signals

---

## Current stance

The watchlist should be:
- small
- curated
- author-weighted
- link-first
- canonicalization-first

This keeps X useful without letting it flood the system with noise.
