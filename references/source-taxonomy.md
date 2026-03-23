# Source Taxonomy and Candidate Inputs

This document turns the latest source-discovery pass into a concrete taxonomy for the v2 evolution discovery system.

Goal:
- avoid uncontrolled source sprawl
- separate stable ingest from discovery-only references
- identify which sources should feed `openclaw-evolution`
- identify which sources should feed `applied-ai-evolution`
- prepare the system for output-layer work later

---

## Core principle

Not every useful page should become a first-class ingest source.

We should classify each candidate into one of four roles:

1. **stable-ingest**
   - suitable for recurring, direct, long-term ingestion
   - official repos, releases, stable feeds, reliable newsletters, structured pages

2. **discovery-index**
   - useful for finding more sources/projects/items
   - not necessarily suitable as direct primary ingest
   - awesome-lists, curated directories, collection pages

3. **trend-intelligence**
   - useful for seeing what is rising / top-base / moving now
   - rankings, growth pages, weekly skill trend systems, star-growth systems

4. **editorial-reference**
   - useful for learning how to write better outputs or understanding human editorial curation
   - newsletters, weekly briefings, radar-style reports, curated summaries

---

## A. `openclaw-evolution` candidates

These are about OpenClaw itself, its skills ecosystem, its registry, and skill/MCP discovery.

### A1. stable-ingest

#### 1. `openclaw/clawhub`
- URL: <https://github.com/openclaw/clawhub>
- Why:
  - official registry core
  - useful for registry capability changes, API shape, metadata evolution, search/versioning ideas
- Suggested role:
  - stable-ingest
  - official-anchor
- Priority: P0

#### 2. `openclaw/skills`
- URL: <https://github.com/openclaw/skills>
- Why:
  - official archive of published skills
  - useful for skill volume, archive structure, versioning, ecosystem scale
- Suggested role:
  - stable-ingest
  - registry-backup
- Priority: P0

#### 3. `openclaw` org overview
- URL: <https://github.com/openclaw>
- Why:
  - useful umbrella signal for official repos and movement
- Suggested role:
  - stable-ingest / official-anchor
- Priority: P1

---

### A2. trend-intelligence

#### 4. `clawhubtrends-rising`
- URL: <https://clawhubtrends.com/rising.html>
- Why:
  - strongest current rising-signal source
  - already has site-specific extractor implemented
  - gives rank / skill / owner / delta / downloads / DL/day / age
- Suggested role:
  - trend-intelligence
  - rising-source
- Priority: P0

#### 5. `topclawhubskills`
- URL: <https://topclawhubskills.com/>
- Why:
  - strong top-base signal
  - already has site-specific extractor implemented
  - gives rank / skill / owner / downloads / stars / installs/day / safety / summary
- Suggested role:
  - trend-intelligence
  - top-base-source
- Priority: P0

#### 6. `last30days-weekly`
- URL: <https://playbooks.com/skills/openclaw/skills/last30days-weekly>
- Why:
  - useful weekly/community/analysis skill intelligence source
  - likely good bridge between trend and editorial layers
- Suggested role:
  - trend-intelligence
  - weekly-intelligence
- Priority: P1

#### 7. `skills-weekly`
- URL: <https://clawhub.ai/ademczuk/skills-weekly>
- Why:
  - useful weekly summary/reference source
  - good candidate for later weekly-mention extraction
- Suggested role:
  - trend-intelligence / editorial-reference
- Priority: P1

---

### A3. discovery-index

#### 8. `VoltAgent/awesome-openclaw-skills`
- URL: <https://github.com/VoltAgent/awesome-openclaw-skills>
- Why:
  - powerful categorized discovery source
  - useful for finding categories and ecosystem breadth
- Suggested role:
  - discovery-index
- Priority: P0

#### 9. `sundial-org/awesome-openclaw-skills`
- URL: <https://github.com/sundial-org/awesome-openclaw-skills>
- Why:
  - alternative category/discovery view
- Suggested role:
  - discovery-index
- Priority: P2

#### 10. `LHL3341/awesome-claws`
- URL: <https://github.com/LHL3341/awesome-claws>
- Why:
  - broader OpenClaw-inspired ecosystem and use-case discovery
- Suggested role:
  - discovery-index
- Priority: P2

---

### A4. editorial-reference

#### 11. `OpenClaw Skills Weekly`-style pages
- Primary URLs:
  - <https://clawhub.ai/ademczuk/skills-weekly>
  - <https://playbooks.com/skills/openclaw/skills/last30days-weekly>
- Why:
  - useful for seeing how humans/skills convert ecosystem motion into interpretable briefings
- Suggested role:
  - editorial-reference
- Priority: P1

---

## B. `applied-ai-evolution` candidates

These are about practical AI workflows, coding-agent ecosystems, project radar, builder tooling, and useful applied patterns.

### B1. stable-ingest

#### 12. `agents-radar`
- URL: <https://github.com/duanyytop/agents-radar>
- Why:
  - one of the strongest direct comparables
  - tracks Claude Code / Codex / Gemini CLI / OpenClaw / GitHub AI trending / official updates
  - close to our product direction
- Suggested role:
  - stable-ingest
  - reference-project
- Priority: P0

#### 13. `coding-cli-tracker`
- URL: <https://github.com/howardpen9/coding-cli-tracker/issues/9>
- Why:
  - weekly issue-based tracking of coding CLI ecosystem
  - useful as recurring signal source and output-structure reference
- Suggested role:
  - stable-ingest / editorial-reference
- Priority: P1

#### 14. `NanoClawRadar`
- URL: <https://github.com/happydog-intj/NanoClawRadar>
- Why:
  - daily automated ecosystem tracking with digests and source config
  - useful as both source/reference and architectural inspiration
- Suggested role:
  - stable-ingest / reference-project
- Priority: P1

#### 15. `GitHubTrendingRSS`
- URL: <https://mshibanami.github.io/GitHubTrendingRSS/>
- Why:
  - already part of current project-radar chain
  - stable base input, though too broad alone
- Suggested role:
  - stable-ingest
- Priority: P0

---

### B2. discovery-index

#### 16. `hesreallyhim/awesome-claude-code`
- URL: <https://github.com/hesreallyhim/awesome-claude-code>
- Why:
  - strong ecosystem discovery index for Claude Code tooling, hooks, slash commands, workflows, MCP-related resources
- Suggested role:
  - discovery-index
- Priority: P0

#### 17. `catlog22/Claude-Code-Workflow`
- URL: <https://github.com/catlog22/Claude-Code-Workflow>
- Why:
  - strong workflow/orchestration reference project
  - useful for multi-agent workflow design and ecosystem adjacency
- Suggested role:
  - discovery-index / applied watchlist
- Priority: P1

#### 18. `poemswe/co-researcher`
- URL: <https://github.com/poemswe/co-researcher>
- Why:
  - useful ecosystem-adjacent multi-platform research suite signal
- Suggested role:
  - discovery-index / applied watchlist
- Priority: P2

#### 19. `alirezarezvani/claude-skills`
- URL: <https://github.com/alirezarezvani/claude-skills>
- Why:
  - broad multi-platform skill/plugin library signal
- Suggested role:
  - discovery-index
- Priority: P2

#### 20. `melodic-software/claude-code-plugins`
- URL: <https://github.com/melodic-software/claude-code-plugins>
- Why:
  - useful plugin ecosystem input
- Suggested role:
  - discovery-index
- Priority: P2

---

### B3. trend-intelligence

#### 21. `GitHub trending` / `GitHubTrendingRSS`
- URLs:
  - <https://github.com/trending>
  - <https://mshibanami.github.io/GitHubTrendingRSS/>
  - <https://duccioo.github.io/GitHubTrendingRSS/>
- Why:
  - useful as broad candidate generation
  - should remain pre-filter candidate flow, not direct final signal
- Suggested role:
  - trend-intelligence
  - candidate generation
- Priority: P0

#### 22. `daily-trending-repo`
- URL: <https://github.com/marc-ko/daily-trending-repo>
- Why:
  - useful as an adjacent project-radar style reference
- Suggested role:
  - trend-intelligence / editorial-reference
- Priority: P2

---

### B4. editorial-reference

#### 23. `OpenDigest`
- URL: <http://opendigest.ai/>
- Why:
  - useful for builder-facing weekly editorial style
- Suggested role:
  - editorial-reference
- Priority: P2

#### 24. `Vibe Coding Weekly`
- URL: <https://vibecodingweekly.substack.com/p/vibe-coding-weekly-21>
- Why:
  - useful for coding-agent / builder weekly output style
- Suggested role:
  - editorial-reference
- Priority: P1

#### 25. `Horizon`
- URL: <https://github.com/Thysrael/Horizon>
- Why:
  - multi-source daily AI briefing reference project
- Suggested role:
  - editorial-reference / reference-project
- Priority: P2

---

## C. Immediate implementation recommendations

### C1. Highest-value next additions

#### For `openclaw-evolution`
Add/keep as the strongest next-layer set:
- `openclaw/clawhub`
- `openclaw/skills`
- `VoltAgent/awesome-openclaw-skills`
- `clawhubtrends-rising`
- `topclawhubskills`
- `last30days-weekly`

#### For `applied-ai-evolution`
Add/keep as the strongest next-layer set:
- `agents-radar`
- `GitHubTrendingRSS`
- `coding-cli-tracker`
- `NanoClawRadar`
- `hesreallyhim/awesome-claude-code`
- `catlog22/Claude-Code-Workflow`

---

### C2. What NOT to do yet

Do not:
- blindly ingest every awesome-list
- treat editorial newsletters as stable core data sources
- keep expanding sources before output design exists
- let discovery-index pages dominate ranking signals

---

## D. Recommended next product move

Now that source candidates are clearer, the next most sensible step is:

### Option 1 — output-layer start
Build the first `openclaw-evolution brief` and/or queue files from the refined trend intelligence.

This would turn:
- source ingest
- trend extraction

into:
- interpretable product output

### Option 2 — Grok fix task
Run a dedicated `search-layer` Grok repair/verification task:
- inspect actual credential location
- validate endpoint / model / auth combination
- verify with one real successful search

### My recommendation
Do both, but in this order:
1. finish source taxonomy (this doc)
2. fix Grok 401 as a separate narrow task
3. start output-layer work

---

## E. Current Grok status

As of the latest validation run, Grok in `search-layer` is still failing with:

- `[grok] error: 401 Client Error: Unauthorized for url: https://marybrown.dpdns.org/v1/chat/completions`

Meaning:
- search-layer overall still works via Exa/Tavily
- Grok is not yet verified working
- do not treat Grok as usable until a real successful search confirms it
