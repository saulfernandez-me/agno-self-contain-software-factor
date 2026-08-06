# 🚀 Features and Technical Specifications

This document outlines the core features, design patterns, and roadmap for the **Agno Self-Contain Software Factor (ASF)**.

---

## 🎨 Key Features

### 1. The `AsfWorkflow` Engine
A specialized extension of Agno's standard `Workflow` that enforces SSSF-style determinism:
*   **State Machine Routing**: Step routing is managed purely by standard Python logic (loops, conditionals), preventing the agent from dictating the graph.
*   **Lane Context Manager**: Uses Python's `with workflow.lane("agent"):` or `with workflow.lane("code"):` to track, style, and log metrics based on the current execution environment.
*   **Built-in Token & Time Tracking**: Automatically logs TTFT (Time to First Token), total latency, and token consumption per lane.

### 2. Pydantic-Driven Contracts (Envelopes)
Strict serialization of input/output boundaries:
*   **`EnvelopeBase` Class**: The standardized data transfer object (DTO) that every cognitive node must output.
*   **Automated Validation**: Integrates directly with Agno's `response_format` or structured outputs to guarantee that the LLM payload conforms to the required Pydantic schema.
*   **Payload Persistence**: Automatically saves envelopes in `.context/runs/<run_id>/envelopes/<phase_id>.json` for auditing and reproducibility.

### 3. Verification Gates
A modular library of assertion checkers:
*   **FileSystem Assertions**: Verify that output paths exist and contain valid contents.
*   **Command Assertions**: Run shell commands (like `pytest` or `ruff check`) and parse stdout/stderr and exit codes to catch syntax and logic errors before phase transitions.
*   **Custom Python Assertions**: Hook up your own custom Python functions to evaluate deep logic or repository states.

### 4. Interactive Correction Engine
A feedback mechanism for failed gates:
*   **Error Structuring**: Converts complex linter warnings, compiler panics, or test failures into a concise, actionable error report.
*   **System Re-Prompt**: Injects the error report back into the agent's chat history with a clear prompt requesting immediate correction of specific files.
*   **Bailout Escalation**: Automatically escalates to a human operator (`kind="engineer"`) if the agent fails to resolve the errors within the designated `max_attempts`.

---

## 📅 Roadmap & Development Plan

```
┌────────────────────────────────────────────────────────┐
│  PHASE 1: Foundations                                   │
│  - Folder structure, CLI boilerplate                    │
│  - EnvelopeBase and basic gate abstractions             │
└───────────┬────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────┐
│  PHASE 2: Engine & Lanes                               │
│  - AsfWorkflow custom implementation                  │
│  - Lane context managers & logging                     │
│  - In-session correction loops                         │
└───────────┬────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────┐
│  PHASE 3: Built-in Agents & CLI                        │
│  - Default Agno developer team configurations         │
│  - Standard execution gates (Linter, Tester)            │
│  - Rich-driven terminal dashboard                      │
└────────────────────────────────────────────────────────┘
```

### Phase 1: Foundations & Architecture (Current)
*   [x] Set up repository structure.
*   [x] Conceptualize SSSF principles inside Agno.
*   [ ] Standardize the Pydantic schemas.

### Phase 2: Orchestration Core
*   [ ] Implement `AsfWorkflow` and lane context managers.
*   [ ] Build the file-system state tracker (`.context/`).
*   [ ] Design the async correction-loop machinery.

### Phase 3: Developer Agents & CLI
*   [ ] Configure default Agno agents (e.g., CodeWriter, CodeAuditor).
*   [ ] Implement the terminal-based Gantt-style execution dashboard.
*   [ ] Add `asf` command-line utility.
