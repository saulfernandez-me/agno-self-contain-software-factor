# Reference: GitHub PDLC Control Plane

> **Purpose:** Defines the standardized label taxonomy and issue templating used to orchestrate APF agents autonomously without manual terminal interaction.

## 1. Issue Label Taxonomy (The State Machine)

APF uses GitHub Issue labels to track the execution state of a workflow. The Python orchestrator (`ApfWorkflow`) listens for these labels and transitions them automatically.

| Label | Executing Node | Description |
| :--- | :--- | :--- |
| `apf:backlog` | Human | Issue created and ready for the factory to pick up. |
| `apf:planning` | `Agent (Planner)` | Creating architectural design. |
| `apf:implementing`| `Agent (Builder)` | Writing source code and tests. |
| `apf:testing` | `Code (Gates)` | Running linters and unit test suites locally. |
| `apf:reviewing` | `Human (HITL)` | PR opened, awaiting human review or merge. |
| `apf:blocked` | `None (Escalation)`| Agent failed the correction loop `max_attempts`. Human rescue needed. |

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
