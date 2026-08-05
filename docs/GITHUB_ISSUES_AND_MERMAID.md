# 🧬 Visual & Issue-Driven Engineering: Mermaid.js & GitHub Issues Framework

This document defines the visual execution and task-driven framework for **Agno Self-Contain Software Factor (ASSF)**. It details how we integrate **Mermaid.js** diagrams to drive workflow creation and how we structure **GitHub Issues** to act as the primary control plane for autonomous agents.

---

## 🎨 1. Mermaid-Driven Workflows: Code-to-Graph & Graph-to-Code

A major innovation of ASSF over standard SSSF is the bidirectional integration of **Mermaid.js** diagrams within the Python workflow execution engine. Instead of treating diagrams purely as static documentation, ASSF uses them as **active execution blueprints**.

```
  +───────────────────────────────────────────+
  |              Visual Blueprint             |
  |             (workflow.mermaid)            |
  +─────────────────────┬─────────────────────+
                        │
                        ▼ [ASSF Compiler]
  +───────────────────────────────────────────+
  |             AssfWorkflow Graph            |
  |         (Deterministic Python Loop)       |
  +─────────────────────┬─────────────────────+
                        │
                        ▼ [Execution & Telemetría]
  +───────────────────────────────────────────+
  |           Live Trace Waterfall            |
  |               (Vue/Vite UI)               |
  +───────────────────────────────────────────+
```

### Pattern A: Graph-to-Code (Blueprints Definition)
Instead of forcing engineers to modify complex Python files to change a pipeline's steps, ASSF includes a `MermaidParser` that compiles a standard Mermaid diagram into a runnable `AssfWorkflow`:

1.  **The Blueprint File (`workflow.mermaid`)**:
    ```mermaid
    graph TD
        subgraph "LANE: agent"
            A["planner: Create implementation steps [Context: docs/]"]:::agent
            C["builder: Write code changes [Context: plan.md]"]:::agent
        end
        subgraph "LANE: code"
            B["assert_file_exists: Verify plans/plan.md"]:::code
            D["assert_tests_pass: Run pytest"]:::code
        end
        A --> B
        B --> C
        C --> D
    ```
2.  **The Compilation**:
    The `AssfWorkflow` class reads this Mermaid file, parses the nodes and edges, validates that no cognitive agent nodes (`:::agent`) sit in code lanes (`subgraph "LANE: code"`), and instantiates the sequential steps in Python.
3.  **The Benefit**: Changing the workflow order or injecting a new validation gate is as simple as adding a line to the Mermaid text.

### Pattern B: Code-to-Graph (Interactive Trace)
When a workflow runs, the `AssfWorkflow` tracer writes a live Mermaid trace file (`.assf/runs/<run_id>/trace.mermaid`) reflecting:
*   **Green Nodos**: Completed phases.
*   **Yellow Nodos**: Active running phases.
*   **Red Nodos**: Failed phases currently in the **Correction Loop**.
*   **Transitions**: Labeled with token counts and latency (e.g., `A -->|3.2k tokens / 1.4s| B`).

This trace is read by the ASSF UI to render a gorgeous, visual status diagram in real-time.

---

## 🎫 2. The GitHub-Driven SDLC Framework

To allow agents to operate autonomously, we replace human project boards with a strict **GitHub Issues Interface**. GitHub Issues act as the input queue, tracking system, and communication channel.

```
[Issue Created] ──> [Label: assf:backlog] ──> [Agent Triggers] ──> [Branch Created]
                                                                        │
[PR Created] ◄── [Correction Loop Passes] ◄── [Gates Evaluated] ◄── [Agent Writes Code]
```

### A. Issue Templates (Templatization)
We enforce strict Markdown issue templates under `.github/issue_template/` to structure inputs for the agents.

#### Template: `.github/issue_template/assf-feature.md`
```markdown
---
name: "🚀 Feature Implementation"
about: "Request a new feature for the agent to design, build, and test."
title: "feat: <title>"
labels: ["assf:backlog"]
---

### 📝 Scope Description
Provide a clear, detailed explanation of what the feature should achieve.

### 🧬 Architectural Requirements
- **Language/Framework**: [e.g., Python, FastAPI]
- **Target Files**: [e.g., `src/api/auth.py`]

### ✅ Definition of Done (Deliverables Checklist)
- [ ] Feature implementation code.
- [ ] Unit tests covering edge cases.
- [ ] No regression failures in the test suite.

### 🧪 Verification Commands
The exact shell command the gate runner should execute to validate your work:
```bash
pytest tests/test_auth.py
```
```

### B. Labels and Lifecycle States
We use GitHub Labels to manage the execution state of the issue board.

| Label | Phase | Executing Agent | Description |
| :--- | :--- | :--- | :--- |
| `assf:backlog` | Queue | None | The issue is ready for processing. |
| `assf:planning` | Recon & Design | `Planner` | The agent is creating a tech design and mapping files. |
| `assf:implementing`| Coding | `Builder` | The agent is writing source code and tests. |
| `assf:testing` | Verification | `Assertion Gates` | Automated gates are running unit tests and linters. |
| `assf:reviewing` | Human Gate | `Reviewer` (Human) | The PR is open and awaiting code review or approval. |
| `assf:blocked` | Escalation | None | Gates failed `max_attempts` or require manual human fix. |
| `assf:done` | Closed | None | PR is merged and code is live. |

### C. The Agent Workflow Loop on GitHub

A dedicated runner (or cron job) executes the following Python loop to process tasks:

1.  **Poll**: Query GitHub API for any open issues labeled `assf:backlog`.
2.  **Assign & Transition**: Assign the issue to the agent, replace the `assf:backlog` label with `assf:planning`.
3.  **Branch Isolation**: Create a clean Git branch locally: `git checkout -b feat/issue-<id>-<slug>`.
4.  **Execute Workflow**:
    *   **Phase 1 (Plan)**: Run `Planner` agent on the issue description. Outputs `plan.md` (Envelope).
    *   **Phase 2 (Build)**: Run `Builder` agent on the plan. Outputs changes.
    *   **Phase 3 (Verify)**: Run local Gates (linter, tests).
        *   *If Fail*: Trigger the **Correction Loop** in-session. If `attempts > max`, remove label, add `assf:blocked`, post error trace as a comment on the issue, and halt.
5.  **Deliver**: Once gates pass, commit changes, push the branch, and open a Pull Request.
6.  **Comment**: Add an execution summary comment on the issue:
    *   Cost breakdown ($).
    *   Total tokens consumed.
    *   List of files touched.
    *   Test runner console snippet showing greens.
7.  **Final Transition**: Relabel the issue as `assf:reviewing` and link the PR.

---

## 🎨 3. Dashboard Spec (The Observability UI)

To bring SSSF's amazing visual telemetry into Agno, we define the **ASSF Dashboard**:

*   **Backend**: A lightweight **FastAPI** server running inside `.assf/` that polls `.assf/data/telemetry.db` (SQLite WAL mode).
*   **Frontend**: A responsive Tailwind Dashboard served on `http://localhost:4600`.

### Key UI Modules:
1.  **Token & Cost Analytics**: Beautiful charts showing cost per run, token efficiency, and cache hit metrics per model.
2.  **Interactive Trace Waterfall**: Shows the execution times and token counts of each phase (`agent` vs `code`) as a Gantt chart.
3.  **Live Transcript View**: Displays the agent conversation, separating the Markdown output from the hidden `<thinking>` blocks of reasoning.
4.  **HITL Approvals Interface**: When a workflow enters the `engineer` lane, the UI halts, displays the git diff produced by the agent, and presents two buttons: **[Approve PR]** or **[Request Changes]** (with a text box to feedback the agent).
