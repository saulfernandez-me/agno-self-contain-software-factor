# Reference: Telemetry Schema and Observability

> **Purpose:** Explains the internal SQLite database structure of APF. Agents can use this knowledge to answer financial, performance, or diagnostic questions from the human engineer.

## 1. The WAL-Mode SQLite Database
All APF executions are traced in real-time to a local SQLite database located at `.context/data/telemetry.db`.
It operates in WAL (Write-Ahead Logging) mode, meaning it is safe to read (query) even while a workflow is currently executing and writing to it.

## 2. Database Schema

The database consists of two primary tables:

### A. The `sessions` Table
Tracks the high-level workflow execution (The overall DAG).
- `id` (TEXT): The unique UUID of the workflow run.
- `name` (TEXT): The name of the workflow (e.g., `standard_pdlc`).
- `started_at` (REAL): Unix timestamp of start.
- `ended_at` (REAL): Unix timestamp of completion.
- `status` (TEXT): `running`, `completed`, or `failed`.

### B. The `phases` Table
Tracks individual lane executions within a workflow.
- `id` (TEXT): The unique UUID of the phase execution.
- `session_id` (TEXT): Foreign key to the `sessions` table.
- `lane` (TEXT): The lane type (`agent`, `code`, `engineer`).
- `started_at` (REAL): Unix timestamp.
- `ended_at` (REAL): Unix timestamp.
- `duration_ms` (REAL): Exact execution time in milliseconds.

## 3. How to Query (For Agents)
If the human engineer asks you: *"How long did the code gates take in the last run?"*, you (the Agent) can use the `run_shell_command` tool (if authorized) to execute a sqlite3 query directly against the file:

```bash
sqlite3 .context/data/telemetry.db "SELECT SUM(duration_ms) FROM phases WHERE lane='code';"
```

**Do not attempt to modify (INSERT/UPDATE) this database.** It is managed exclusively by the `ApfWorkflow` Python engine.
