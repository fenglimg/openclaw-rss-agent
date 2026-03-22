# Prompt Patterns

## Triage prompt

Given a list of RSS items, classify each item as:
- send
- digest
- drop

Prefer:
- implementation details
- tool releases
- workflows
- concrete lessons
- items strongly relevant to the user's tracked topics

Avoid:
- repetitive low-information news
- vague opinion posts
- clickbait
- duplicates

Return JSON:

```json
[
  {
    "id": "item-id",
    "decision": "digest",
    "score": 0.78,
    "reason": "Relevant to OpenClaw/RSS automation"
  }
]
```

## Summary prompt

For each selected item, produce:
- one-line takeaway
- 2-4 bullets
- do not invent facts
- include the original link separately
