# Reference: GitHub SDLC Control Plane

> **Purpose:** Defines the standardized label taxonomy and issue templating used to orchestrate ASSF agents autonomously without manual terminal interaction.

## 1. Issue Label Taxonomy (The State Machine)

ASSF uses GitHub Issue labels to track the execution state of a workflow. The Python orchestrator (`AssfWorkflow`) listens for these labels and transitions them automatically.

| Label | Executing Node | Description |
| :--- | :--- | :--- |
| `assf:backlog` | Human | Issue created and ready for the factory to pick up. |
| `assf:planning` | `Agent (Planner)` | Creating architectural design. |
| `assf:implementing`| `Agent (Builder)` | Writing source code and tests. |
| `assf:testing` | `Code (Gates)` | Running linters and unit test suites locally. |
| `assf:reviewing` | `Human (HITL)` | PR opened, awaiting human review or merge. |
| `assf:blocked` | `None (Escalation)`| Agent failed the correction loop `max_attempts`. Human rescue needed. |

## 2. Issue Templating

To ensure the agent receives structured requirements, you must use standard GitHub Issue Templates (`.github/ISSUE_TEMPLATE/`).

A template must include a designated section for the **Verification Command**. This tells the Code Lane exactly what gate to run to consider the issue "Done".

### Markdown Block Example:
```markdown
### 🧪 Verification Commands
The exact shell command the gate runner should execute to validate your work:
` ` `bash
uv run pytest tests/test_module.py
` ` `
```
*(Note: backticks spaced above to prevent markdown parser escaping).*
