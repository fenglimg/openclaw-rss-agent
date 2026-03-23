# V2 Architecture — Evolution Discovery System on top of ClawFeed

## Purpose

This document defines the next-phase architecture for this project.

The system is no longer treated as a simple RSS digest tool.
Instead, it becomes a **discovery system** built on top of the `clawfeed` base, with two main evolution tracks:

1. **OpenClaw self-evolution materials**
2. **Personal applied-AI self-evolution materials**

The key idea is:

- `clawfeed` provides the durable platform base
- source systems provide stable recall
- profile/rules provide first-stage narrowing
- `search-layer` provides validation / expansion / discovery
- agents provide judgment / abstraction / adoption reasoning
- outputs are not only digests, but also adoption-oriented queues

---

## Product identity

This project should be understood as:

## an evolution discovery system

not merely:

- an RSS reader
- a simple AI digest
- a one-pass ranking script

The system should continuously discover, validate, prioritize, and surface materials that are useful for:

- OpenClaw capability evolution
- personal applied-AI workflow evolution

---

## Two main profiles

The entire system should be organized around two top-level discovery profiles.

---

### Profile A — `openclaw-evolution`

### Goal

Surface materials that OpenClaw itself could absorb, reuse, productize, or learn from.

### Typical interests

- OpenClaw workflows and new usage patterns
- skills and skill patterns
- MCP servers and MCP interaction patterns
- agent orchestration ideas
- automation and delivery patterns
- Claude Code / Codex / Gemini features worth borrowing into OpenClaw workflows
- community pain points that could become product or skill improvements
- candidate docs / playbooks / product capabilities

### Core question

> What should OpenClaw absorb, improve, or learn from today?

### Preferred outputs

- today’s absorbable discoveries
- candidate capabilities
- candidate skills
- candidate workflows
- candidate documentation upgrades
- candidate product ideas
- observe / research / adopt queue entries

---

### Profile B — `applied-ai-evolution`

### Goal

Surface practical, reliable, application-layer materials that help the user improve their own AI usage and workflows.

### Typical interests

- OpenClaw / Claude Code / Codex / Gemini CLI new uses
- old features used in new ways
- workflow breakthroughs
- real repairs / workarounds / setup guides
- GitHub projects with large stars or meaningful star growth
- useful templates / scaffolds / starter repos
- practical Chinese community usage patterns
- reliable, reproducible, non-hype discovery

### Core question

> What is new, practical, reliable, and worth trying today?

### Preferred outputs

- today’s highlights
- important updates
- applied workflow discoveries
- GitHub project radar
- community practical signals
- save / try / follow-up suggestions

---

## Why profiles are necessary

Without profiles, all signals collapse into one blended digest and the system becomes muddy.

Profiles make it possible to vary:

- source packs
- ranking priorities
- candidate buckets
- output sections
- adoption semantics
- delivery cadence

Profiles should be treated as first-class architecture, not just optional labels.

---

## Source layer

The source layer should provide broad but stable recall.

### Source classes

Examples include:

- RSS / Atom feeds
- GitHub releases / changelogs / repo activity
- GitHub trending sources
- official websites / official blogs
- Hacker News / community sites
- Linux.do / V2EX / Chinese community sources
- ClawHub / skill ecosystem signals
- curated digest/reference sources

### Principle

The source layer should optimize for:

- steady recall
- broad coverage
- low fragility

It should **not** attempt to make all nuanced product judgments.

---

## Candidate pipeline

The candidate pipeline should transform raw inputs into high-value, profile-specific opportunities.

The pipeline should be structured in phases.

---

### Phase 1 — Ingest

Input:

- raw source items from RSS / GitHub / community / official web / ecosystem feeds

Output:

- normalized raw items

Responsibilities:

- fetch
- normalize
- dedupe
- store minimal source metadata

---

### Phase 2 — Profile pre-triage

Each profile should apply a first-stage narrowing pass.

### Responsibilities

- core-ecosystem matching
- practical signal matching
- source trust weighting
- novelty hints
- community practical hints
- GitHub project hints
- reject obvious noise early

### Output

- profile-specific candidate pools

This phase should be rule-driven and relatively cheap.

---

### Phase 3 — Candidate bucketization

Candidates should not be processed as one flat list.

Each profile should organize candidates into semantic buckets.

---

## Candidate buckets

Candidate buckets make later agent judgment more balanced and less easily dominated by one source type.

### Shared / general buckets

#### 1. `important_updates`

Examples:

- releases
- changelogs
- feature updates
- integration changes
- migration notes
- important official updates

#### 2. `applied_workflows`

Examples:

- setup guides
- recipes
- templates
- scaffolds
- workflow combinations
- workaround / repair / integration patterns

#### 3. `project_radar`

Examples:

- large-base important GitHub repos
- fast-growing repos
- template / scaffold / MCP / skill / workflow repos
- repos worth following or trying

#### 4. `community_practice`

Examples:

- Linux.do practical discussions
- HN practical discoveries
- V2EX practical threads
- author-blog practical usage reports

---

### Profile-specific bucket extensions

#### For `openclaw-evolution`

Add:

- `candidate_skill`
- `candidate_workflow_capability`
- `candidate_docs_upgrade`
- `candidate_product_capability`
- `candidate_ecosystem_signal`

#### For `applied-ai-evolution`

Add:

- `candidate_try_now`
- `candidate_fix_or_workaround`
- `candidate_follow_project`
- `candidate_high_signal_repo`

---

### Why bucketization matters

If everything is one list, one strong source can dominate.
If candidates are bucketed, the system can preserve diversity and force balanced selection.

---

## Search-layer role

`search-layer` should be integrated as a **secondary discovery and validation layer**, not as the primary feed chain.

### Search-layer should NOT do

- replace stable source ingest
- run against every low-value item
- become the default fetch mechanism for all content

### Search-layer SHOULD do

#### 1. Candidate validation

For strong candidates:

- cross-source confirmation
- official-source confirmation
- related issue / PR / blog / article discovery
- detect whether a signal is isolated or truly spreading

#### 2. Context expansion

For high-value candidates:

- add surrounding context
- connect repo, issue, release, article, and community discussion
- reduce title-only decision errors

#### 3. Source discovery

From strong candidates:

- discover new related feeds
- discover related project sources
- discover related official or community signals

### Typical trigger conditions

Search-layer should run on:

- top candidates per bucket
- ambiguous but potentially important items
- community-originated workaround / fix signals
- project radar candidates
- candidate skill / adoption opportunities

---

## Agent role

Agents should not be used as raw source ingestors.
Agents should be used where judgment, abstraction, and adoption reasoning matter.

### Agent SHOULD do

#### 1. novelty judgment

Questions:

- Is this genuinely new?
- Is this just a repeated story?
- Is this hype or a real new use?
- Is this old knowledge with no new information?

#### 2. adoption judgment

Questions:

- Should OpenClaw absorb this?
- Can this become a skill, workflow, docs improvement, or product capability?
- Should the user try this now?
- Is this worth saving, monitoring, or ignoring?

#### 3. semantic classification

Questions:

- Is this a workflow candidate?
- a skill candidate?
- a project candidate?
- a fix / workaround candidate?
- a candidate docs improvement?
- just a weak signal?

#### 4. synthesis

Questions:

- Why does this matter?
- What changed?
- What should be done next?
- Which profile should care more?

### Agent SHOULD NOT do

- process every item from raw ingest
- replace cheap rule-based pre-triage
- become the only source of ranking

Agents should operate on narrowed candidate sets.

---

## Quality dimensions

The system should evaluate high-value candidates using dimensions stronger than keyword relevance.

### 1. `applicability_score`

How directly usable is this?

Signals include:

- concrete commands
- setup steps
- integration steps
- repair / workaround details
- templates / scaffolds / starter repos
- reproducible workflows

### 2. `novelty_score`

How new or insight-rich is this?

Signals include:

- old feature in a new use pattern
- newly emerged workaround
- newly practical integration
- strong information gain over familiar stories

### 3. `adoptability_score`

How likely is it that this can be absorbed into OpenClaw or the user’s real workflows?

Signals include:

- candidate skill
- candidate workflow
- candidate docs update
- candidate project to follow
- candidate operational pattern

### 4. `signal_quality_score`

How trustworthy and non-generic is this?

Signals include:

- source quality
- cross-source validation
- non-repetitive information
- concrete details rather than impressions
- not dominated by hype or commodity discussion

---

## Output layer

The system should have multiple output targets.

A digest alone is not enough.

---

### Output A — Briefing / Digest

This is the human-readable output.

#### For `applied-ai-evolution`

Suggested sections:

1. today’s highlights
2. important updates
3. applied workflow discoveries
4. GitHub project radar
5. community practice / repairs / tips

#### For `openclaw-evolution`

Suggested sections:

1. today’s absorbable discoveries
2. candidate capabilities
3. candidate skills / workflows
4. ecosystem changes worth watching
5. community pain points / repair patterns
6. suggested adoption / observation actions

---

### Output B — Adoption queue

This is essential for `openclaw-evolution`.

Candidates should be triaged into statuses such as:

- adopt now
- research more
- convert to skill candidate
- convert to workflow candidate
- convert to docs candidate
- observe only
- ignore

This queue is what turns the system into a genuine self-evolution material pipeline.

---

### Output C — Deep-dive queue

Some candidates should be marked for deeper analysis.

Use cases:

- promising new project worth full review
- emerging workflow pattern worth mapping
- community pain point worth tracing across issues and docs
- candidate source worth adding into a source pack

---

## How this fits on top of ClawFeed

`clawfeed` should provide the platform base:

- source system
- source packs
- storage / persistence
- digest infrastructure
- dashboard
- OpenClaw skill compatibility

This project should add a discovery layer above that base.

### Conceptual layering

#### Layer 1 — ClawFeed base

- source definitions
- subscriptions
- persistence
- feed/digest platform
- dashboard

#### Layer 2 — Discovery logic

- profiles
- candidate buckets
- novelty / applicability / adoptability / quality signals
- search-layer enrichment triggers
- agent judgment pipeline

#### Layer 3 — Product outputs

- evolution briefs
- applied briefs
- adoption queues
- deep-dive queues
- later: delivery / Discord routing / channel-specific formatting

---

## Implementation strategy

The next implementation phase should not begin with broad feature copying.

Instead:

### Step 1

Define and preserve the profile layer clearly.

### Step 2

Implement the minimum structure for:

- two profiles
- candidate buckets
- output targets

### Step 3

Integrate search-layer as a selective enrichment layer.

### Step 4

Integrate agent judgment only on narrowed candidate sets.

### Step 5

Then stitch in external strengths module by module:

- GitHub radar
- skill / MCP trend ingestion
- community practical signals
- clustering / narrative grouping

---

## Reference-project stitching principle

When borrowing from external projects:

- compare concrete strengths and weaknesses first
- absorb the useful module, not the whole worldview
- integrate by profile goal and pipeline role
- avoid turning the system into a patchwork of mismatched identities

In short:

## stitch strengths, not identities

---

## Short summary

The future system should work like this:

1. broad source recall
2. profile-specific pre-triage
3. candidate bucketization
4. selective search-layer enrichment
5. agent novelty / adoption / synthesis judgment
6. digest + queue outputs

This is the intended architecture for building an evolution discovery system on top of `clawfeed`.
