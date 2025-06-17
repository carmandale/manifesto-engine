╭──────────────────────── PLAN TEMPLATE ─────────────────────────╮
│ Generate PLAN only – no code, no execution.                   │
╰────────────────────────────────────────────────────────────────╯

OUTPUT FORMAT (JSON):
```json
{
  "prd_id": "PRD-YYYY-ABC-XYZ",
  "title": "Project Name",
  "tasks": [
    {
      "id": "TASK-001",
      "description": "≤12 words summary",
      "depends_on": [],
      "owner_role": "DEV-AGENT"
    }
    // up to 8 tasks total
  ]
}
```

Constraints:
• Exactly match field names.
• Max 8 tasks.
• Descriptions ≤ 12 words.
• Do not include acceptance tests here – they live in manifesto. 