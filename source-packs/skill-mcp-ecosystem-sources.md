# Skill & MCP Ecosystem — Candidate Input Sources

This file lists the first candidate input sources for the `skill-mcp-ecosystem` source pack.

## High-priority candidates

### 1. openclaw/skills
- URL: <https://github.com/openclaw/skills>
- Why: official backup/archive of registry skills; useful for ecosystem-wide discovery and structure scanning.
- Use for:
  - candidate skill discovery
  - registry trend observation
  - category / topic mining

### 2. VoltAgent/awesome-openclaw-skills
- URL: <https://github.com/VoltAgent/awesome-openclaw-skills>
- Why: large categorized curation layer over the skill ecosystem.
- Use for:
  - category discovery
  - high-signal skill references
  - finding niches / clusters

### 3. OpenClaw Skills Weekly
- URL: <https://clawhub.ai/ademczuk/skills-weekly>
- Why: directly tracks trending ClawHub skills and generates weekly intelligence.
- Use for:
  - movers / rockets style trend signals
  - ranking logic reference
  - snapshot accumulation ideas

### 4. last30days-weekly
- URL: <https://playbooks.com/skills/openclaw/skills/last30days-weekly>
- Why: combines snapshot-based skill intelligence with broader community research.
- Use for:
  - trend research workflow reference
  - community buzz integration
  - weekly signal generation ideas

### 5. Rising Skills — ClawHub Trends
- URL: <https://clawhubtrends.com/rising.html>
- Why: explicit rising-skill view with growth signals.
- Use for:
  - velocity / growth candidate ingestion
  - quick trend shortlist

### 6. Top ClawHub Skills / Top OpenClaw Hub Rankings
- URLs:
  - <https://topclawhubskills.com/>
  - <https://openclaw-hub.org/openclaw-hub-top-skills.html>
- Why: gives top installs / downloads / stars style rankings.
- Use for:
  - large-base important skills
  - ranking baselines
  - popularity vs growth comparison

## Secondary candidates

### 7. LeoYeAI/openclaw-master-skills
- URL: <https://github.com/LeoYeAI/openclaw-master-skills>
- Why: curated weekly-updated skill collection.
- Use for:
  - curated examples
  - ecosystem surface scan

### 8. ClawHub registry itself
- URL: <https://github.com/openclaw/clawhub>
- Why: useful for understanding registry structure and future integration points.
- Use for:
  - metadata model understanding
  - registry-aware ingestion design

## First implementation recommendation

Start the `skill-mcp-ecosystem` chain with three signal types:

1. rising / fast-moving skills
2. top-base / widely-installed skills
3. curated/category-discovery sources

That will give a balanced first candidate pool for `openclaw-evolution`.
