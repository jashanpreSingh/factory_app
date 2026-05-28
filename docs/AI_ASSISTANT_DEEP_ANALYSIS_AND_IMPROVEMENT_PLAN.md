# Factory AI Assistant Deep Analysis and Improvement Plan

## Purpose

This document reviews the current backend AI assistant implementation and defines how to make it answer all important Factory app questions more accurately, safely, and consistently while remaining read-only.

The current implementation lives mainly in:

- `ai_assistant/views.py`
- `ai_assistant/serializers.py`
- `ai_assistant/services.py`
- `ai_assistant/tests.py`
- `config/settings.py`
- `config/urls.py`

## Current Implementation Summary

The assistant exposes one authenticated endpoint:

```text
POST /api/v1/ai/assistant/chat/
```

Request body:

```json
{
  "question": "How many GRPOs are pending?",
  "page": "/grpo/pending"
}
```

The endpoint requires:

- JWT authentication through DRF.
- A valid `Company-Code` header through `HasCompanyContext`.
- `GEMINI_API_KEY` for model-backed answers.

The assistant has three answer modes.

### 1. Local Direct Answers

The fastest and safest path is direct Django ORM logic. It handles known questions such as:

- Pending GRPO counts.
- Finished goods receipt counts.
- Gate entry counts.
- GRPO posting counts.
- Production run counts.
- Weighment counts.
- BOM request counts.
- Barcode box and pallet counts.

Strengths:

- Does not depend on model-generated SQL.
- Uses company-scoped ORM filters.
- Gives deterministic answers for common count questions.
- Avoids provider calls for some common questions.

Weaknesses:

- Coverage is manual and incomplete.
- It is mostly count/status oriented.
- It does not yet handle many natural app questions like "which entries are delayed today", "what should store do next", or "show open maintenance work orders by urgency".

### 2. Curated Context + Gemini Answer

When there is no direct answer, the service builds a limited JSON context and asks Gemini to answer from that context.

Current curated context includes:

- Barcode boxes.
- Barcode pallets.
- Label print logs.
- Production releases from SAP.
- Pending GRPOs.
- Vehicle gate entries.
- Security checks.
- Raw material PO receipts.
- GRPO postings.
- Quality control.
- Weighment.
- Production.
- Warehouse BOM requests and finished goods receipts.
- Selected document snippets.

Strengths:

- Safer than unrestricted database access.
- The answer can include explanation, next checks, and operational guidance.
- Context is limited by `AI_ASSISTANT_MAX_CONTEXT_ROWS`.

Weaknesses:

- Some app modules are not represented with rich curated context.
- The model only sees small samples, so it may miss full-database trends unless SQL mode runs.
- Document search is hardcoded to a few paths and does not index the existing repo docs.

### 3. Guarded Read-Only SQL Mode

For broad analysis questions, Gemini generates SQL from a schema context. The backend validates the SQL, executes it in a read-only transaction, caps rows, then asks Gemini to summarize the result.

Current protections:

- Only `SELECT` or `WITH` statements are allowed.
- Semicolons, SQL comments, and many write/admin keywords are blocked.
- Sensitive identifiers such as password, token, secret, session, credential, and API keys are blocked.
- Table references must be in the Django-derived allowed schema.
- Company-scoped table references must include a company filter.
- PostgreSQL transactions are marked read-only.
- Query results are capped by `SQL_RESULT_ROW_LIMIT`.
- PostgreSQL statement timeout is set locally for SQL execution.

Strengths:

- Can answer deeper data questions than local context.
- Uses real database data instead of only samples.
- Has a useful first layer of SQL safety.

Weaknesses:

- SQL validation still depends heavily on regex and `sqlparse`.
- The normal application database connection is used.
- Any authenticated user with company context can currently trigger SQL mode.
- There is no audit log for generated SQL, blocked SQL, or user questions.
- The schema exposed to the model is raw technical schema, not a business semantic model.

## Important Current Gaps

### 1. Module Coverage Is Incomplete

The Factory app has many modules:

- Accounts and company access.
- Driver and vehicle management.
- Security checks.
- Raw material gate-in.
- Weighment.
- Quality control.
- Daily needs gate-in.
- Maintenance gate-in.
- Construction gate-in.
- Person gate-in.
- GRPO.
- Production execution.
- SAP plan dashboard.
- Stock dashboard.
- Inventory age.
- Dispatch plans.
- Non-moving raw material.
- Warehouse.
- Barcode.
- Notifications.

The assistant has good coverage for barcode, GRPO, QC, weighment, production, warehouse, raw material, gate entries, and security checks. But daily needs, maintenance, construction, person gate-in, dispatch plans, inventory age, non-moving RM, SAP plan dashboard, stock dashboard, and notifications need stronger curated contexts.

### 2. Person Gate-In Is Not Clearly Company-Scoped

Most vehicle-related modules can be scoped through `VehicleEntry.company`. Person gate-in models such as `EntryLog`, `Visitor`, `Labour`, `Contractor`, `Gate`, and `PersonType` do not show a direct company field in the reviewed model file.

This matters because SQL mode requires company filtering for company-scoped data. If a module has no reliable company relationship, the assistant may either:

- Avoid useful answers.
- Or risk cross-company visibility if not handled carefully.

Recommendation: add explicit company scoping to person gate-in data or define a clear safe scoping rule before including it in AI SQL and curated context.

### 3. SQL Mode Needs Stronger Authorization

The assistant endpoint requires authentication and company context, but SQL mode is broader than normal page-level access. It can answer across many allowed business tables.

Recommendation: split permissions:

- Normal assistant context answers: available to authenticated company users.
- Deep database analysis / SQL mode: only users with a dedicated permission, for example `ai_assistant.can_query_factory_database`.

### 4. The Assistant Does Not Yet Know Business Workflows Deeply

The model sees data but not enough business meaning. For example:

- Which status means "pending action" in each module?
- Which statuses are final?
- Which date field should be used for ageing?
- Which document number should users search by?
- Which joins are valid for a business question?
- Which module owns the next action?

Without this semantic layer, the assistant may answer technically correct but operationally weak responses.

### 5. Date Understanding Is Too Implicit

Users will ask:

- "today"
- "yesterday"
- "this week"
- "last month"
- "pending since 7 days"
- "delayed more than 24 hours"

The current prompt does not provide normalized date boundaries to the model. This can lead to inconsistent SQL and answers.

### 6. Document Search Is Too Limited

The repo already contains many module docs under `docs/` and app-specific `docs/` folders. Current document search only checks a few hardcoded files outside or near the backend.

For "how to use this module" or "what is this API flow" questions, the assistant should search indexed app docs first.

### 7. No Feedback or Evaluation System Exists

There is no persisted question log, answer rating, or golden test set. Without this, improvement will be guesswork.

The assistant needs a way to measure:

- Which questions users ask.
- Which questions fail.
- Which modules are weak.
- Which SQL validations block useful questions.
- Which answers users mark as helpful or wrong.

## Target Behavior

The best version of this assistant should:

1. Answer operational questions from live app data.
2. Explain how to use each module.
3. Guide users to the next action without changing data.
4. Respect company boundaries.
5. Respect user permissions.
6. Never expose secrets, credentials, tokens, passwords, or private configuration.
7. Avoid hallucinating actions, postings, approvals, labels, or SAP writes.
8. Clearly say when data is missing or permission is denied.
9. Give short answers for simple questions and structured analysis for deep questions.
10. Cite the source type used, such as local context, app docs, or read-only SQL.

## Recommended Architecture

Use a layered answer pipeline.

```text
User question
  -> authenticate and resolve company
  -> classify intent
  -> check user permission for requested scope
  -> retrieve context from the safest suitable source
  -> answer
  -> log question, answer mode, source, and errors
```

Recommended answer modes:

1. `local_direct`
   - Deterministic ORM functions for common counts, statuses, and latest records.

2. `module_context`
   - Curated ORM snapshots for specific modules.

3. `docs_rag`
   - Indexed backend docs for "how to", API, workflow, and troubleshooting questions.

4. `semantic_query`
   - Structured query planner over approved datasets.

5. `readonly_sql`
   - Fallback for advanced users only, protected by dedicated permission, parser validation, audit logs, and read-only DB credentials.

## Highest Priority Improvements

### 1. Add a Dedicated SQL Permission

Add an `ai_assistant` permission such as:

```text
ai_assistant.can_query_factory_database
```

Behavior:

- All authenticated company users can ask normal assistant questions.
- Only users with this permission can trigger SQL mode.
- Users without this permission should still get local/direct/context answers.

Why this is important:

- SQL mode can analyze broad operational data.
- It should be treated like a management/reporting capability.

### 2. Use a Dedicated Read-Only Database User

Add a second database alias, for example:

```python
DATABASES["ai_readonly"] = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": config("AI_DB_NAME"),
    "USER": config("AI_DB_USER"),
    "PASSWORD": config("AI_DB_PASSWORD"),
    "HOST": config("AI_DB_HOST"),
    "PORT": config("AI_DB_PORT", default="5432"),
}
```

The database user should only have `SELECT` permissions on approved tables.

Why this is important:

- Application-level validation is not enough by itself.
- If validation has a bug, the database should still reject writes.

### 3. Replace Regex SQL Validation With AST Validation

Keep current checks, but add a proper SQL parser such as `sqlglot`.

Validate:

- Statement type is only `SELECT`.
- No DDL, DML, function calls with side effects, comments, or multiple statements.
- All table references are allowlisted.
- All selected columns are allowlisted.
- Company filter is present and structurally valid.
- Query contains a safe limit for list-style answers.

Best long-term option:

Do not let the model generate SQL directly. Let it generate a structured query plan:

```json
{
  "dataset": "grpo_postings",
  "metrics": ["count"],
  "dimensions": ["status"],
  "filters": [
    {"field": "company_id", "op": "=", "value": 1}
  ],
  "date_range": {
    "field": "created_at",
    "from": "2026-05-01",
    "to": "2026-05-28"
  }
}
```

Then backend code converts this into ORM or SQL using allowlisted datasets and fields.

### 4. Add AI Audit Logging

Create an `AIQueryLog` or `AIAssistantInteraction` model.

Recommended fields:

- `user`
- `company`
- `question`
- `page`
- `intent`
- `mode`
- `provider`
- `model`
- `generated_sql`
- `validation_status`
- `blocked_reason`
- `row_count`
- `latency_ms`
- `error_code`
- `created_at`

Do not store full SQL result rows by default.

Benefits:

- Debug wrong answers.
- Track usage by module.
- Detect repeated failed questions.
- Prove read-only behavior.
- Improve prompts and tests using real examples.

### 5. Build a Semantic Schema Registry

Add `ai_assistant/schema_registry.py`.

Each dataset should define:

- Business label.
- Django model.
- Table name.
- Company scope path.
- Allowed fields.
- Hidden fields.
- Search fields.
- Status field.
- Default date field.
- Common filters.
- Common metrics.
- Safe joins.
- Example questions.

Example:

```python
DATASETS = {
    "vehicle_gate_entries": {
        "label": "Vehicle Gate Entries",
        "model": "driver_management.VehicleEntry",
        "company_filter": "company_id",
        "default_date": "entry_time",
        "search_fields": ["entry_no", "vehicle__vehicle_number", "driver__name"],
        "status_field": "status",
        "allowed_metrics": ["count", "latest", "status_breakdown"],
    },
    "maintenance_gate_entries": {
        "label": "Maintenance Gate Entries",
        "model": "maintenance_gatein.MaintenanceGateEntry",
        "company_filter": "vehicle_entry__company_id",
        "default_date": "created_at",
        "search_fields": ["work_order_number", "supplier_name", "material_description", "equipment_id"],
        "status_field": "vehicle_entry__status",
        "allowed_metrics": ["count", "latest", "urgency_breakdown"],
    },
}
```

This will make answers more accurate because the assistant will use business concepts instead of guessing from raw column names.

## Module-by-Module Improvements

### Barcode

Current coverage is good for boxes, pallets, labels, status counts, and print history.

Improve by adding:

- Box ageing by manufacturing date and expiry date.
- Near-expiry and expired stock answers.
- Pallet utilization answers.
- Dispatch readiness answers.
- Label reprint troubleshooting from `LabelPrintLog`.
- Barcode movement history context.
- Questions by batch, item, warehouse, production line, and status.

Example questions to support:

- "Where is box BOX-... now?"
- "Which pallets are incomplete?"
- "How many boxes expire this month?"
- "Which labels were printed today?"
- "Why is this box not dispatchable?"

### GRPO

Current coverage is good for pending GRPO counts and postings.

Improve by adding:

- PO-wise pending lines.
- Supplier-wise pending GRPO.
- Failed GRPO error grouping.
- Posted vs pending trend by day.
- Reconciliation between PO receipt and GRPO posting.
- Service GRPO support if service modules are included.

Example questions:

- "Which pending GRPO is oldest?"
- "Show suppliers with most failed GRPO."
- "Which POs are pending for entry GE-...?"
- "Why did GRPO posting fail?"

### Raw Material Gate-In

Current coverage includes PO receipt counts and matching records.

Improve by adding:

- Pending gate completion.
- PO item level context.
- Supplier/material summaries.
- Invoice/challan duplicate checks.
- Entries waiting for weighment, QC, or GRPO.

Example questions:

- "Which raw material entries are still open?"
- "Which supplier has most entries this week?"
- "Show entries received without QC."

### Weighment

Current coverage includes completed and incomplete counts.

Improve by adding:

- Gross-only pending tare.
- Tare-only invalid cases.
- Net weight variance checks.
- Missing weighbridge slip answers.
- Average turnaround time from gate entry to weighment.

Example questions:

- "Which vehicles are waiting for second weight?"
- "Which entries have missing slip numbers?"
- "What is the average net weight by supplier?"

### Quality Control

Current coverage includes arrival slip and inspection statuses.

Improve by adding:

- Workflow stage ownership.
- Material-wise pass/fail/reject.
- Supplier-wise rejection rate.
- Pending inspection ageing.
- Send-back/factory-head decision summaries.
- Internal lot number search.

Example questions:

- "Which QC inspections are pending approval?"
- "Which supplier has most rejections?"
- "Find report number for internal lot ..."
- "Which materials are waiting for factory head decision?"

### Production Execution

Current coverage includes runs, breakdowns, waste, line clearance, and warehouse approval status.

Improve by adding:

- Line-wise production efficiency.
- Planned vs actual production.
- Breakdown duration and active issue summary.
- Waste reason analysis.
- Line clearance pending checks.
- SAP sync failure summaries.
- Production order linkage.

Example questions:

- "Which production runs are stuck?"
- "Which line has highest waste?"
- "Show active breakdowns."
- "Why is this production run not complete?"

### Warehouse

Current coverage includes BOM requests and finished goods receipts.

Improve by adding:

- BOM line shortages.
- Material issue status by production run.
- FG receipt pending SAP posting.
- Warehouse-wise FG receipt summary.
- SAP error grouping for FG receipts.

Example questions:

- "Which BOM requests are pending approval?"
- "Which production runs have not received material?"
- "Which FG receipts failed SAP posting?"

### Daily Needs Gate-In

Current gap: not included as a rich curated context.

Add context for:

- `DailyNeedGateEntry`
- `DailyNeedGateEntryItem`
- `CategoryList`
- Linked `VehicleEntry`
- Department, supplier, material, quantity, unit, bill, challan.

Direct answers:

- Count by status.
- Count by category.
- Latest daily need entries.
- Department-wise material receipt.
- Pending completion.
- Supplier-wise summary.

Example questions:

- "How many daily needs entries came today?"
- "Which canteen materials were received this week?"
- "Show pending daily need gate entries."

### Maintenance Gate-In

Current gap: not included as a rich curated context.

Add context for:

- `MaintenanceGateEntry`
- `MaintenanceType`
- Linked `VehicleEntry`
- Work order number.
- Supplier.
- Equipment ID.
- Urgency level.
- Receiving department.

Direct answers:

- Count by urgency.
- Pending/completed work orders.
- Equipment-wise maintenance material.
- Department-wise maintenance entries.
- Latest critical entries.

Example questions:

- "Show critical maintenance entries."
- "How many maintenance items are pending?"
- "Find work order WO-2026-001."

### Construction Gate-In

Current gap: not included as a rich curated context.

Add context for:

- `ConstructionGateEntry`
- `ConstructionMaterialCategory`
- Linked `VehicleEntry`
- Project, contractor, material, quantity, approval status.

Direct answers:

- Security approval status counts.
- Project-wise material receipt.
- Contractor-wise receipt.
- Pending approval list.

Example questions:

- "Which construction entries are pending security approval?"
- "How much cement came for project X?"
- "Show entries by contractor."

### Person Gate-In

Current gap: not included as a rich curated context and company scoping needs attention.

Before enabling broad AI answers, define company scoping for:

- `EntryLog`
- `Visitor`
- `Labour`
- `Contractor`
- `Gate`
- `PersonType`

Then add context for:

- Inside vs exited persons.
- Visitor vs labour counts.
- Gate-wise movement.
- Contractor-wise labour inside.
- Blacklisted visitors.
- Expired permit or contract risk.

Example questions:

- "How many visitors are inside?"
- "Which labours have not exited?"
- "Show contractor-wise labour count inside."
- "Any blacklisted visitor entered today?"

### Dispatch Plans

Current gap: not included in curated assistant context.

Add context for:

- Dispatch plan status.
- Linked vehicle entry.
- Driver and transporter.
- Invoice fields.
- Bilty attachment.
- Service GRPO defaults.
- AP invoice posting status if available.

Example questions:

- "Which dispatch plans are not linked to vehicle entry?"
- "Which invoices are pending dispatch?"
- "Which transporter bills need posting?"

### SAP Plan Dashboard, Stock Dashboard, Inventory Age, Non-Moving RM

These modules are dashboard/reporting oriented and should be first-class AI datasets.

Add context for:

- SAP plan summaries.
- Stock by item/warehouse.
- Inventory ageing buckets.
- Non-moving raw material summaries.

Example questions:

- "Which raw materials are non-moving?"
- "Which warehouse has highest old stock?"
- "Show stock risk by item."
- "What production plan is pending?"

### Notifications

Add limited context for:

- Unread notifications.
- Failed notification delivery if tracked.
- Stale FCM token cleanup status.

Avoid exposing device tokens or private notification credentials.

Example questions:

- "How many unread notifications do I have?"
- "Which notification type is most common?"

## Prompt Improvements

### System Prompt Rules

Add stronger global rules:

- "You are read-only. Never say you created, updated, approved, posted, printed, synced, cancelled, or deleted anything."
- "If a user asks for a write action, explain where in the app they can perform it if they have permission."
- "Use exact app object names when known: GRPO, Vehicle Entry, Material Arrival Slip, Production Run, BOM Request, FG Receipt."
- "If the question depends on a date phrase, use the normalized date context."
- "If the data source is a sample, say that the answer is based on the available context."
- "If permission blocks data, say permission is required."

### Date Context

Before calling Gemini, compute:

```json
{
  "timezone": "Asia/Kolkata",
  "today": "2026-05-28",
  "yesterday": "2026-05-27",
  "this_week_start": "2026-05-25",
  "this_month_start": "2026-05-01",
  "last_7_days_start": "2026-05-22",
  "last_30_days_start": "2026-04-29"
}
```

Pass this to both context and SQL planning prompts.

### Answer Format

Use consistent answer shapes:

Simple count:

```text
There are 12 pending GRPO entries.
```

List:

```text
I found 5 matching entries:
1. GE-001 - Pending - ABC Supplier
2. GE-002 - Completed - XYZ Supplier
```

Deep analysis:

```text
Summary: ...
Key findings: ...
Risks: ...
Next checks: ...
```

Permission denied:

```text
You do not have permission to view pending GRPO entries.
```

Missing data:

```text
I could not find matching records for this company. Check the entry number, date range, or module.
```

## Retrieval and Documentation Improvements

### Index Existing Docs

The repo already has many useful docs:

- `docs/`
- `accounts/docs/`
- `gate_core/docs/`
- `raw_material_gatein/docs/`
- `quality_control/docs/`
- `production_execution/docs/`
- `warehouse` docs and related guide files.
- `barcode` rules and reports.
- `grpo/docs/`
- `notifications/docs/`
- Other module-specific docs.

Build a local docs index:

- Scan Markdown files.
- Split into chunks by heading.
- Store title, path, heading, module, and content.
- Use keyword search first.
- Later add embeddings if needed.

For now, a simple indexed keyword retriever will be much better than hardcoded document paths.

### Add Source Citations

For documentation answers, return source metadata:

```json
{
  "type": "document",
  "label": "grpo/docs/workflow.md",
  "heading": "Posting Flow"
}
```

For data answers, return source metadata:

```json
{
  "type": "factory_database",
  "label": "GRPO postings, PO receipts, vehicle entries"
}
```

## Security and Privacy Checklist

Implement these before enabling broad production usage:

- Dedicated SQL permission.
- Dedicated read-only database user.
- SQL AST validation or structured query planner.
- Audit logging.
- PII review for user, visitor, labour, driver, and contact fields.
- Module-level permission checks before retrieving context.
- Company scoping for every dataset.
- Sensitive field allowlist, not only denylist.
- Query timeout and row limit.
- No full result-row logging by default.
- Provider prompt should not include secrets or credentials.
- Do not expose `settings`, env variables, SAP credentials, FCM credentials, JWT tokens, passwords, or API keys.

## Testing Plan

### Unit Tests

Add tests for:

- Intent classification.
- Date phrase normalization.
- Module context builders.
- Direct answers per module.
- Permission-gated SQL mode.
- SQL validator blocks writes.
- SQL validator blocks sensitive fields.
- SQL validator blocks unknown tables.
- SQL validator requires company scope.
- SQL validator blocks cross-company queries.
- Provider errors are returned cleanly.

### Golden Question Tests

Create a fixed list of expected questions per module.

Examples:

- "How many GRPOs are pending?"
- "Show latest raw material gate entries."
- "Which QC inspections are rejected?"
- "Which vehicles are waiting for weighment?"
- "Which production runs are in progress?"
- "Which FG receipts failed SAP posting?"
- "How many visitors are inside?"
- "Which construction entries are pending approval?"
- "Which maintenance entries are critical?"
- "How do I post GRPO?"

Each test should assert:

- Correct mode.
- Correct source.
- No provider call when local answer is expected.
- Company isolation.
- No sensitive fields in answer.

### Integration Tests

Use DRF API tests for:

- Auth required.
- `Company-Code` required.
- Wrong company rejected.
- SQL permission required for SQL mode.
- Read-only behavior.
- Fallback when Gemini fails.

## Implementation Roadmap

### Phase 1: Safety Foundation

1. Add SQL mode permission.
2. Add AI interaction audit log.
3. Add read-only database alias.
4. Add module-level permission checks before context retrieval.
5. Add date context helper.

### Phase 2: Better App Coverage

1. Add curated contexts for daily needs, maintenance, construction, and person gate-in.
2. Add contexts for dispatch plans, inventory age, stock dashboard, non-moving RM, and SAP plan dashboard.
3. Add direct answer handlers for common counts, statuses, latest records, and pending actions.
4. Improve document search to scan repo Markdown docs.

### Phase 3: Smarter Querying

1. Build `schema_registry.py`.
2. Replace raw schema prompt with semantic dataset prompt.
3. Move from model-generated SQL to model-generated structured query plans.
4. Convert approved query plans to ORM queries.
5. Keep raw SQL mode only for admins or remove it once structured querying is strong enough.

### Phase 4: Evaluation and Continuous Improvement

1. Add golden question tests.
2. Add answer feedback fields.
3. Review failed questions weekly.
4. Add missing direct answers based on real usage.
5. Track answer mode success rates.

## Recommended First Code Changes

Start with these because they reduce risk and improve answer quality quickly:

1. Add `AIAssistantInteraction` model and migration.
2. Add `can_query_factory_database` permission.
3. Block SQL mode unless the user has that permission.
4. Add curated contexts for:
   - daily needs
   - maintenance
   - construction
   - person gate-in after company scoping is confirmed
5. Add a docs index over existing Markdown files.
6. Add normalized date context to all prompts.
7. Add tests for all of the above.

## Example Final Assistant Capability

After these improvements, the assistant should answer questions like:

- "How many GRPOs are pending today?"
- "Which pending GRPO is oldest?"
- "Why did the latest GRPO fail?"
- "Which raw material entries are waiting for QC?"
- "Which vehicles have incomplete weighment?"
- "Which QC supplier has highest rejection?"
- "Which production run is blocked by warehouse?"
- "Which FG receipts failed SAP posting?"
- "Which maintenance entries are critical?"
- "Which construction entries need security approval?"
- "How many visitors are currently inside?"
- "Which stock is non-moving?"
- "How do I complete a daily need gate entry?"
- "What API should frontend call for barcode dispatch?"

The answer should be short when the question is simple, detailed when the user asks for analysis, and always clear about whether it used local data, documentation, or read-only database analysis.

## Final Recommendation

The current implementation is a strong first version because it is read-only, company-aware, and already combines ORM context with guarded SQL. To make it production-grade, focus first on permission separation, audit logging, read-only database credentials, semantic dataset definitions, and richer module contexts. These changes will make the assistant safer and much better at answering real Factory app questions across every module.
