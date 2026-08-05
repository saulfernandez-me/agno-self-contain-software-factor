# 🤖 ASSF Agent Directive & Rules (AGENTS.md) 🏭✨

This repository is **Agno Self-Contain Software Factor (ASSF)**, a rigid and deterministic software factory framework built on top of the **Agno SDK**, implementing **Super Simple Software Factory (SSSF)** methodologies.

---

## 🌐 1. Language Rule: Strict English Boundary (NON-NEGOTIABLE 🚦)

To ensure this software factory is enterprise-ready, maintainable, and aligned with international open-source standards, we enforce a strict language protocol:

*   **Code**: All variable names, class names, method names, comments, docstrings, and logs **MUST** be written strictly in English.
*   **Documentation**: All `.md` files, diagrams, specifications, and architecture records **MUST** be written strictly in English.
*   **Git Interactions**: All commit messages (following Conventional Commits), branches (`feat/`, `fix/`, `docs/`, `chore/`), and Pull Request titles/descriptions **MUST** be written strictly in English.
*   **Agent Cognition & Internal Reasoning**: Any subagent chain or execution runner inside this factory must process prompts and outputs in English.
*   **User Communication Exception 💬**: While all codebase files, commits, and PRs must be 100% English, the agent (**Tachikoma**) may continue to interact with **Yachar-sama** in Spanish during chat sessions to preserve their personal bond, unless explicitly asked otherwise.

---

## 🏛️ 2. Architectural Pillars (SSSF Integration)

Every agent operating within this repository must strictly adhere to the five core pillars of ASSF:

1.  **Graph Sovereignty**:
    *   Never let an agent decide its own routing or choose the next file to process in a freeform loop.
    *   The orchestration graph is defined in deterministic Python (`AssfWorkflow` subclassing `Workflow`).
    *   Agents are subordinate cognitive nodes invoked strictly inside Python methods.

2.  **Explicit Execution Lanes**:
    *   Never mix CPU-deterministic logic with LLM cognition.
    *   Separate execution states into `agent` (LLM-based reasoning), `code` (local bash scripts, linters, tests), and `engineer` (human approvals).

3.  **Physical Pydantic Envelopes**:
    *   Handoffs between agents/nodes must be serialized to disk as a structured JSON file matching an `EnvelopeBase` Pydantic class.
    *   No raw chat transcript handoffs. Clear input/output data boundaries only.

4.  **Assertion Gates**:
    *   An agent task is never finished because the agent says so. It is finished when local assertion tests (linters, unit tests, custom scripts) confirm factual success.
    *   Every `agent` lane output must be immediately followed by a `code` lane validation gate.

5.  **In-Session Correction Loops**:
    *   Do not kill the process on a failed gate. Use the active session history to re-prompt the agent with structured error reports until it corrects the issue, up to `max_attempts`.

---

## 🛠️ 3. Coding Standards & Tooling

When writing Python code for ASSF, always follow these standards:
- **Environment & Execution**: Use `uv` as the package and environment manager.
- **Python Version**: Minimum Python 3.10.
- **Frameworks**:
  - **Agno SDK**: Core agentic framework.
  - **Pydantic v2**: High-performance data validation.
  - **Typer / Rich**: CLI interfaces and beautiful terminal dashboards.
- **Linter & Formatter**: Rely on `ruff` for code linting and formatting.

---

## 📈 4. Conventions for Commits and PRs

*   **Commits**: Strictly follow the Conventional Commits specification.
    *   `feat: ...` for new features or capabilities.
    *   `fix: ...` for bugs or broken gates.
    *   `docs: ...` for documentation files.
    *   `refactor: ...` for code restructuring.
    *   `chore: ...` for configuration files or system updates.
*   **Pull Requests**: Must be opened autonomously by the executing agent. Keep descriptions technical, specifying the affected phases, gates, and envelopes.
