# Judgment Calibration Rules v1

This document captures reusable calibration rules discovered while building and tuning both:

- `openclaw-evolution`
- `applied-ai-evolution`

It exists so the system does not need to re-learn the same borderline judgments manually every time.

The goal is to convert one-off calibration insights into repeatable decision guidance.

---

## Why this exists

The system now has:
- source ingest
- rules pre-filter
- search-layer enrichment
- source normalization
- source judgment
- output-layer judgments
- targeted calibration on borderline items

Without a reusable calibration layer, future edge cases will still require manual interpretation.

This document turns recent calibration results into explicit reusable judgment rules.

---

## Scope

These rules are not replacements for:
- source ingest
- source judgment
- search-layer enrichment

They are a final adjustment layer for borderline content judgments such as:
- `adopt`
- `follow`
- `deep-dive`
- `official-anchor`
- `adopt-candidate`

---

## Rule Family A — Tooling Surface Upgrade

### Pattern
A candidate is a **tooling surface** and has:
- repeated GitHub confirmations
- ecosystem-list references (awesome list / marketplace / plugin index)
- evidence of adjacent author ecosystem or sibling projects
- direct practical utility in a real workflow

### Default calibration
Upgrade from:
- `follow`

Toward:
- `adopt`

### Why
Tooling surfaces often become valuable faster than abstract frameworks because:
- user value is concrete
- practical utility is easier to infer
- ecosystem fit is easier to observe

### Example
- `jarrodwatts/claude-hud`
  - repeated GitHub confirmations
  - adjacent author projects like `claude-delegator`
  - awesome/plugin list references
  - clear tooling utility around Claude Code visibility

### Rule shorthand
**tooling surface + author ecosystem + awesome/plugin refs → upgrade pressure toward adopt**

---

## Rule Family B — Methodology / Framework-to-Study

### Pattern
A candidate is a **framework / methodology / meta-workflow system** with:
- strong discussion signal
- releases / changelog activity
- community references
- broad conceptual relevance

But its product lesson is less direct than a tooling surface.

### Default calibration
Prefer:
- `follow`
- with explicit subtype: `framework-to-study` or `methodology`

Avoid automatically upgrading to:
- `adopt`

### Why
Frameworks and methodologies often matter as:
- design references
- process inspirations
- study targets

rather than as direct capability adoption targets.

### Example
- `gsd-build/get-shit-done`
  - strong methodology signal
  - clear spec-driven/context-engineering value
  - but not obviously a direct product capability to adopt unchanged

### Rule shorthand
**methodology/framework signal → strong follow, not direct adopt by default**

---

## Rule Family C — Strong Support, Weak Lesson Clarity

### Pattern
A candidate has:
- strong source support
- canonical references
- ecosystem presence

but the reusable product lesson is still unclear.

### Default calibration
Prefer:
- `follow`

Avoid upgrading to:
- `adopt`

unless the reusable lesson becomes clearer.

### Why
Support strength alone does not equal product clarity.
A system should not promote a candidate only because it is well represented in sources.

### Example
- `Gog`
  - strong source/ecosystem support
  - but less obvious reusable lesson than browser/search/summarize surfaces

### Rule shorthand
**strong support but unclear reusable lesson → keep follow**

---

## Rule Family D — Behavior-Layer Capability Upgrade

### Pattern
A candidate is a **behavior-layer capability** with:
- canonical ecosystem support
- strong strategic relevance to agent behavior
- reusable implications for product design

### Default calibration
Upgrade from:
- `follow`

Toward:
- `adopt-candidate`

and potentially `adopt` if support continues to strengthen.

### Why
Behavior-layer capabilities often map directly to the assistant/product behavior users want:
- proactive execution
- self-improvement
- follow-through
- memory/correction loops

These are often more strategically important than domain-specific skills.

### Example
- `Proactive Agent`
  - strong canonical references
  - strategically relevant behavioral capability
  - should not be treated as a low-priority generic follow item

### Rule shorthand
**behavior-layer capability + canonical ecosystem support → upgrade toward adopt-candidate**

---

## Rule Family E — Official Anchor Separation

### Pattern
A candidate is an official core product, such as:
- `anthropics/claude-code`
- `openai/codex`
- `google-gemini/gemini-cli`

### Default calibration
Prefer:
- `official-anchor`

Avoid mixing into:
- practical `adopt`
- generic `follow`

unless explicitly judging product usage itself.

### Why
Official anchors are critical to track, but they play a different role from:
- practical frameworks
- plugins
- templates
- orchestration tools

### Rule shorthand
**official product baseline → official-anchor, not ordinary adopt candidate**

---

## Rule Family F — Domain-Specific Signal Caution

### Pattern
A candidate shows strong movement but is domain-specific:
- prediction markets
- weather
- vertical search
- narrow app integrations

### Default calibration
Prefer:
- `deep-dive`
- or `follow`

Avoid direct `adopt` unless a broader reusable lesson is clear.

### Why
High movement can reflect narrow domain novelty rather than durable product pressure.

### Example
- `Polymarket`
- `Weather`

### Rule shorthand
**domain-specific heat without clear reusable lesson → deep-dive**

---

## Rule Family G — Risk Signal Dampening

### Pattern
A candidate has:
- issue/discussion risk signals
- deleted / suspect / trust-related references
- ambiguous registry status

### Default calibration
Add downgrade pressure:
- `adopt` → `adopt-candidate` or `follow`
- `follow` → `deep-dive`

### Why
Risk/evidence objects should influence judgment even when the candidate is otherwise attractive.

### Example
- `self-improving-agent` retained high relevance, but risk/evidence should prevent naive top ranking

### Rule shorthand
**risk/evidence signal present → dampen confidence**

---

## Operational guidance

These rules should be applied after:
1. source ingest
2. rules pre-filter
3. search-layer enrichment
4. source normalization
5. source judgment

They should act as a calibration pass on borderline items.

---

## Recommended implementation shape

### Minimal implementation option
Add a small calibration layer that checks:
- item category
- source-role counts
- presence of author ecosystem references
- presence of awesome/plugin/directory references
- presence of risk/evidence objects
- whether the product lesson is direct vs indirect

### Possible outputs
- `adopt`
- `adopt-candidate`
- `follow`
- `framework-to-study`
- `official-anchor`
- `deep-dive`

---

## Current confirmed examples

### Upgrade examples
- `jarrodwatts/claude-hud` → upgrade pressure toward `adopt`
- `Proactive Agent` → upgrade pressure toward `adopt-candidate`

### Hold examples
- `gsd-build/get-shit-done` → hold at `follow`, but mark as framework/methodology
- `Gog` → hold at `follow`, because lesson clarity remains weak

### Separate-lane examples
- `anthropics/claude-code` → `official-anchor`
- `openai/codex` → `official-anchor`
- `google-gemini/gemini-cli` → `official-anchor`

---

## How this should influence existing scripts

### For `applied-ai-evolution`
Bias toward upgrading when:
- tooling surface
- workflow template
- plugin/tool with author ecosystem
- awesome/plugin references present

Bias toward holding when:
- methodology/framework with indirect product lesson

Separate into `official-anchor` when:
- official baseline product

### For `openclaw-evolution`
Bias toward upgrading when:
- behavior-layer capability
- canonical support exists
- lesson is directly reusable in assistant behavior

Bias toward holding when:
- strong support exists but lesson remains fuzzy

Bias toward deep-dive when:
- domain-specific heat dominates
- risk/evidence signals exist

---

## Final principle

The system should not only ask:
- “How strong is the signal?”

It should also ask:
- “What kind of thing is this?”
- “Is the lesson direct or indirect?”
- “Is this a product capability, a framework, a reference, an anchor, or just evidence?”

That is what calibration is for.
