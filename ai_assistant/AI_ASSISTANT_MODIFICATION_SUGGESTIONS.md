# AI Assistant Modification Suggestions

## Current State

The Factory AI assistant currently has three answer paths:

1. **Local direct answers**
   - Uses curated Django ORM context for known questions like GRPO counts, FG receipt counts, barcode boxes, pallets, warehouse, QC, production, and gate data.
   - This is fast and safer because it does not ask the model to create SQL.

2. **Guarded read-only SQL answers**
   - For broader questions such as insights, trends, comparisons, and deep analysis, Gemini proposes a SQL query.
   - The backend validates the query, blocks write keywords, blocks sensitive identifiers, restricts tables, applies company scoping checks, executes in a read-only transaction, caps rows, then asks Gemini to summarize the result.

3. **General context answers**
   - If no direct or SQL answer is used, Gemini answers from the curated context JSON.

The frontend now renders assistant replies with basic Markdown formatting for paragraphs, bullets, numbered lists, bold labels, and inline code.

## Highest Priority Changes

### 1. Add a Dedicated Permission for SQL Mode

**Why:** Any authenticated user with company context can currently reach the deep SQL path. Even though it is read-only, this gives broad analytical access to many tables.

**Modify:**
- `ai_assistant/models.py` or a new permission carrier model.
- `ai_assistant/migrations/`.
- `ai_assistant/services.py`.
- `ai_assistant/tests.py`.

**Suggested behavior:**
- Keep normal assistant questions available to all authenticated users.
- Only allow read-only SQL mode for users with a permission such as:
  - `ai_assistant.can_query_factory_database`

**Implementation idea:**
```python
if self._should_use_database_query(question) and not self.user.has_perm(
    'ai_assistant.can_query_factory_database'
):
    return {}
```

This lets non-privileged users still get local/context answers without exposing broad database analysis.

### 2. Use a Dedicated Read-Only Database User

**Why:** The application database user can write data. The current code uses a read-only transaction, but defense should be layered. If a validator bug ever slips through, the database user should still be unable to write.

**Modify:**
- `.env`
- `config/settings.py`
- `ai_assistant/services.py`

**Suggested behavior:**
- Add a second Django database alias, for example `ai_readonly`.
- Configure it with a PostgreSQL user that only has `SELECT` permissions on approved tables.
- Execute assistant SQL using that connection alias only.

**Recommended env keys:**
```env
AI_DB_NAME=factory
AI_DB_USER=factory_ai_readonly
AI_DB_PASSWORD=...
AI_DB_HOST=...
AI_DB_PORT=5432
```

### 3. Replace Regex-Only SQL Validation With a Stronger SQL Parser or Query Builder

**Why:** Regex checks are useful but not enough for long-term safety. SQL can hide complexity in CTEs, functions, casts, subqueries, and aliases.

**Modify:**
- `ai_assistant/services.py`
- `requirement.txt`
- `ai_assistant/tests.py`

**Suggested options:**
- Use a parser such as `sqlglot` to inspect AST nodes.
- Or avoid model-generated SQL entirely and let Gemini output a structured query plan that your code converts into ORM/SQL.

**Preferred long-term approach:**
```json
{
  "dataset": "gate_entries",
  "metrics": ["count"],
  "dimensions": ["entry_type", "status"],
  "filters": [
    {"field": "company_id", "op": "=", "value": 1}
  ]
}
```

Then backend code builds the query from allowed datasets, fields, joins, metrics, and filters.

### 4. Add Audit Logging for Every AI SQL Query

**Why:** Management and admins should know who asked what, which SQL was executed, how many rows came back, and whether validation blocked anything.

**Modify:**
- Add `AIQueryLog` model.
- Add migrations.
- Write logs in `FactoryAssistantService._answer_from_database`.

**Fields to track:**
- user
- company
- question
- page
- mode
- generated_sql
- validation_status
- blocked_reason
- row_count
- provider_model
- created_at

Do not store full result rows unless explicitly required, because results may contain operationally sensitive data.

## Data Quality and Intelligence Improvements

### 5. Create a Semantic Schema Registry

**Why:** The model currently sees raw table and column names. It can answer more accurately if it knows business meanings, safe joins, date columns, status values, and default metrics.

**Modify:**
- Add `ai_assistant/schema_registry.py`.
- Use it from `FactoryAssistantService._database_schema_context`.

**Include for each dataset:**
- business name
- table name
- allowed columns
- hidden columns
- company filter path
- date column
- default sort column
- common metrics
- common joins

**Example:**
```python
DATASETS = {
    "daily_need_gate_entries": {
        "label": "Daily Need Gate Entries",
        "table": "driver_management_vehicleentry",
        "company_filter": "company_id",
        "default_date": "entry_time",
        "description": "Vehicles entering for routine operational daily needs.",
        "allowed_dimensions": ["status", "entry_type"],
        "allowed_metrics": ["count"],
    }
}
```

### 6. Add Curated Context for Daily Need, Maintenance, Construction, and Person Gate-In

**Why:** These modules are in the allowed SQL apps, but not all of them have rich local context builders. For common gate questions, direct ORM context is faster, safer, and more reliable than SQL generation.

**Modify:**
- `ai_assistant/services.py`

**Add context builders for:**
- daily needs gate-in
- maintenance gate-in
- construction gate-in
- person gate-in

**Add direct answers for:**
- status counts
- latest entries
- pending/in-progress entries
- category-wise breakdown
- date-wise entry trends

### 7. Add Date Understanding Defaults

**Why:** Users will ask questions like "today", "yesterday", "this week", "last month", and "pending since 7 days". The SQL prompt does not currently provide explicit date rules.

**Modify:**
- `ai_assistant/services.py`

**Suggested behavior:**
- Parse date phrases before calling Gemini.
- Pass a normalized date context into the prompt.
- Use timezone `Asia/Kolkata`.

**Example context:**
```json
{
  "today": "2026-05-08",
  "this_week_start": "2026-05-04",
  "last_30_days_start": "2026-04-08",
  "timezone": "Asia/Kolkata"
}
```

## Reliability Improvements

### 8. Retry SQL Planning Once With Validation Feedback

**Why:** If Gemini generates a query that fails validation, the assistant currently skips SQL mode and falls back. A one-time repair pass can improve success rate while staying safe.

**Modify:**
- `FactoryAssistantService._answer_from_database`

**Suggested behavior:**
1. Generate SQL.
2. Validate SQL.
3. If validation fails, ask Gemini once to fix it using the validation error.
4. Validate again.
5. Execute only if valid.

Never execute a repaired query unless it passes the same validator.

### 9. Cache Schema Context

**Why:** `_database_schema_context()` scans Django models on every deep question. This is okay for development, but unnecessary overhead in production.

**Modify:**
- `ai_assistant/services.py`

**Suggested behavior:**
- Cache schema context for 5 to 15 minutes.
- Include company id only outside the cached schema if needed.

### 10. Add Provider Health Diagnostics

**Why:** DNS/network failures already happened. The UI should be able to distinguish missing API key, DNS failure, quota error, and model error.

**Modify:**
- Add an endpoint such as `/api/v1/ai/assistant/health/`.
- Or add a management command `check_ai_provider`.

**Check:**
- API key configured
- DNS resolves `generativelanguage.googleapis.com`
- minimal Gemini call succeeds
- configured model is available

## UX Improvements

### 11. Add Table Rendering for Assistant Responses

**Why:** Insight answers often contain status breakdowns, top suppliers, date-wise counts, and comparisons. Tables are easier to read than bullets for these.

**Modify:**
- `FactoryFlow/src/modules/ai/components/AiAssistantWidget.tsx`

**Suggested support:**
- Markdown tables
- compact key-value blocks
- source badges with table names

### 12. Show "Rows Capped" Clearly for List Answers

**Why:** SQL results are capped at 50 rows. Users may think they are seeing all records.

**Modify:**
- Backend response metadata.
- Frontend widget source/metadata display.

**Suggested UI:**
- Show "Showing first 50 rows" when `context_summary.database_query.row_count` reaches the cap.

### 13. Improve Suggested Questions by Page

**Why:** Current suggestions are mostly barcode-focused, even when the user is on Gate, QC, Warehouse, or Production pages.

**Modify:**
- `FactoryFlow/src/modules/ai/components/AiAssistantWidget.tsx`

**Examples:**
- Gate page: "Show daily need entries by status"
- QC page: "Which materials are awaiting chemist approval?"
- Warehouse page: "Which FG receipts failed SAP posting?"
- Production page: "Show production runs with high wastage"

## Testing Improvements

### 14. Add Security Tests for SQL Mode

**Modify:**
- `ai_assistant/tests.py`

**Add tests for:**
- SQL without company filter is rejected.
- Cross-company data does not leak.
- Sensitive fields are rejected.
- Multiple statements are rejected.
- SQL comments are rejected.
- CTEs with unsupported tables are rejected.
- Unknown tables are rejected.
- Forbidden functions such as `pg_sleep` are rejected.
- Non-privileged users cannot use SQL mode once permission gating is added.

### 15. Add Accuracy Tests for Common Business Questions

**Modify:**
- `ai_assistant/tests.py`

**Questions to test:**
- "How many daily need entries are in progress?"
- "Show pending GRPO by supplier"
- "How many FG receipts are SAP posted?"
- "Which QC inspections are rejected?"
- "Show production run status summary"
- "Which boxes are active in warehouse FG01?"

These can be tested with mocked Gemini SQL planning and real test database rows.

## Recommended Implementation Order

1. Add permission gating for SQL mode.
2. Add dedicated read-only DB connection.
3. Add audit logging.
4. Add semantic schema registry.
5. Add curated context for daily need, maintenance, construction, and person gate-in.
6. Add SQL retry with validation feedback.
7. Add table rendering and dynamic suggested questions.
8. Expand SQL security tests and common business question tests.

## Production Readiness Checklist

- [ ] SQL mode permission is separate from normal assistant access.
- [ ] SQL executes through a database user with only `SELECT` permissions.
- [ ] SQL validator uses AST-level inspection or structured query plans.
- [ ] Query logs are stored for audit.
- [ ] Company isolation is tested.
- [ ] Sensitive fields are never included in schema prompts or results.
- [ ] Provider health check exists.
- [ ] User-facing errors distinguish DNS, quota, API key, and timeout.
- [ ] Frontend displays row limits and sources clearly.
- [ ] Common business questions have regression tests.

