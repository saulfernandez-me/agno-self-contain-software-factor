<!--
⚠️ HUMAN ENGINEER NOTICE: 
This AI.md (or CLAUDE.md) file is the "System Prompt" for the entire repository.
Autonomous agents (ASF, Cursor, Claude Code) read this file before modifying ANY code.
If agents make repetitive mistakes, DO NOT complain in chat. Add a hard rule here.
Treat this file as your team's collective technical memory.
-->

# 🧠 Repository Context & Agent Instructions

## 1. System Ontology (Purpose & Scope)
- **Domain:** [e.g., Software Engineering / Agroforestry / RPG Content]
- **Core Purpose:** [What does this repository do in one sentence?]
- **Anti-Goals (Out of Scope):**
  - [What should the agent NEVER try to build or solve here?]
  - [e.g., "Do not handle user authentication, that is done at the API Gateway."]

## 2. Tech Stack & Dependencies
- **Primary Language/Environment:** [e.g., Python 3.10+, TypeScript 5.0]
- **Package Manager:** [e.g., uv, pnpm]
- **Core Frameworks:** [e.g., FastAPI, Agno, React]
- **Banned/Forbidden Libraries:** 
  - [e.g., "Never use `requests`, always use `httpx`."]

## 3. Architectural Invariants (Unbreakable Rules)
Agents MUST adhere to these structural rules. Violations will fail the Reviewer Gate.
- [e.g., "All data transfer objects must be Pydantic v2 BaseModels."]
- [e.g., "Business logic must reside in `src/services/`, never in the API routers."]
- [e.g., "Do not use global mutable state."]

## 4. Testing & Definition of Done (DoD)
Before emitting a "success" Envelope, you must ensure your work passes these criteria:
- **Test Runner:** [e.g., `uv run pytest`]
- **Linter/Formatter:** [e.g., `uv run ruff check .`]
- **Coverage Requirement:** [e.g., "New features must include unit tests."]

## 5. Active Workflows (ASF)
This repository uses the Agno Self-Contain Software Factor (ASF).
To execute a task, use one of the pre-configured workflow runners located in `workflows/`:
- `standard_sdlc`: Use for complex feature implementation.
- `bug_fix_loop`: Use for isolated bug resolution.
