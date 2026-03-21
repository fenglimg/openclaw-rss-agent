# Integration Roadmap

## Completed
- RSS fetch / normalize
- dedupe and state tracking
- digest generation
- heuristic triage with general-tech and agentic modes
- per-feed triage config
- topic model config
- source and language policy adjustments
- delivery and cron design docs

## Next recommended step

### Search-layer enrichment v1
Implement a post-triage validation stage for a small number of top candidates.

Expected first implementation pieces:
1. candidate selector
2. enrichment config section
3. validator interface / stub
4. score adjustment merge logic
5. optional structured debug output

## Later steps
- new-term discovery using search-layer
- source discovery suggestions
- weekly promotion / demotion assistant
- cross-source dedup and story clustering
