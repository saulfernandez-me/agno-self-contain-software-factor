# 🏛️ Technical Architecture: ASSF

This document details the architectural design and structural choices behind the **Agno Self-Contain Software Factor (ASSF)** framework. It explains how we bridge the low-level agentic capabilities of **Agno** with the rigid constraints of the **Super Simple Software Factory (SSSF)**.

---

## 🏛️ The 5 Pillars of ASSF

```
+-----------------------------------------------------------------------+
|                       ASSF RUNTIME GRAPH                              |
|                                                                       |
|  +--------------------+      +-----------------+      +------------+  |
|  |     Agent Lane     |      |    Code Lane    |      | Human Lane |  |
|  | (Agno Cognition)   |      | (Bash/Scripts)  |      |   (HITL)   |  |
|  +---------+----------+      +--------+--------+      +-----+------+  |
|            |                          |                     |         |
|            ▼ [Pydantic Contract]      ▼                     ▼         |
|      (JSON Envelope)                  |                     |         |
|            │                          │                     │         |
|            ▼                          │                     │         |
|     [Assertion Gates] ◄───────────────┘                     │         |
|            │                                                │         |
|      PASS? ├──► Yes ──► [Next Phase] ◄──────────────────────┘         |
|            │                                                          |
|            └──► No ───► [In-Session Correction Loop] ──► (Re-Prompt)   |
+-----------------------------------------------------------------------+
```

### Pillar 1: Graph Sovereignty (Deterministic Python Execution)
*   **The Problem:** Letting an LLM decide what tool or script to run next leads to unpredictable behavior, infinite loops, and hallucinated paths.
*   **The ASSF Solution:** The orchestration engine is written in pure Python. The agents are treated as pure "cognitive nodes" inside the workflow.
*   *Implementation in Agno:* Instead of letting agents freely call tools that jump between files, the pipeline is modeled as an `AssfWorkflow` (extending Agno's `Workflow`). Each step is a Python function that invokes a specific agent, captures its output, and handles state transitions deterministically.

### Pillar 2: Strictly Divided Execution Lanes
*   **The Problem:** Mixing cognitive tasks, automated terminal scripts, and human decisions into a single chat thread creates chaotic execution states.
*   **The ASSF Solution:** We partition tasks into three mutually exclusive lanes:
    1.  `kind="agent"`: Pure LLM cognition. Requires reasoning, reading context, and proposing solutions.
    2.  `kind="code"`: Deterministic local scripts (linters, test runners, git operations) running at native CPU speed with zero token cost.
    3.  `kind="engineer"`: Human-in-the-loop (HITL) gate for approvals or manual modifications.

### Pillar 3: Physical Contracts via Pydantic Envelopes
*   **The Problem:** Passing huge raw conversational contexts between agents introduces noise, instruction-following degradation, and is highly token-inefficient.
*   **The ASSF Solution:** The output of an `agent` phase is not plain text; it is a structured, Pydantic-validated JSON file called an **Envelope** written to disk. The next agent or script *only* reads this file.
*   *Envelope Base Schema:*
    ```python
    from pydantic import BaseModel, Field
    from typing import Literal, List, Dict, Any

    class EnvelopeBase(BaseModel):
        status: Literal["success", "fail"]
        summary: str = Field(..., description="A short summary of what this phase achieved")
        artifacts: List[str] = Field(default_factory=list, description="List of physical file paths created or edited")
        metadata: Dict[str, Any] = Field(default_factory=dict, description="Execution and token metrics")
        notes_for_next_agent: str = Field(..., description="Direct technical instructions for the subsequent node")
    ```

### Pillar 4: Post-Phase Assertion Gates (DoD Enforcement)
*   **The Problem:** An agent claiming *"I have finished writing the server code"* is not proof of success.
*   **The ASSF Solution:** Every `agent` phase is immediately followed by a `code` phase running **Assertion Gates**. These are unit tests, static code checkers, or file system assertions that run locally.
*   *Core Gates:*
    *   `ArtifactsExistGate`: Confirms every file declared in the envelope actually exists in the workspace.
    *   `NonEmptyGate`: Verifies the mutated files have real content and are not placeholders.
    *   `LinterGate`: Runs linters (e.g., `ruff`, `eslint`) to ensure syntax compliance.
    *   `TestRunnerGate`: Executes unit/integration tests and checks exit codes.

### Pillar 5: In-Session Correction Loops
*   **The Problem:** Tearing down the agent container and starting a fresh run from scratch on failure is expensive, slow, and discards valuable context.
*   **The ASSF Solution:** If an assertion gate fails, the workflow does not abort. Instead, it re-prompts the active agent session in-place with a structured JSON containing the precise failures. The agent resolves the errors and emits a new envelope. This loop repeats up to a configurable `max_attempts` limit.

---

## 🛠️ Tech Stack & Dependencies

The project relies on:
- **Python 3.10+** (Modern async Python features)
- **Agno SDK** (Agentic frameworks, tools, and workflows)
- **Pydantic v2** (For robust data validation and serialization)
- **Typer / Rich** (For beautiful terminal outputs and CLI interfaces)
- **UV** (For ultra-fast, modern package management)
