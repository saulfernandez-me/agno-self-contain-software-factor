# 🤖 Agno Software Factor (APF) 🏭✨

> **APF** is a rigid, reliable, and deterministic Product Factory framework built on top of the **Agno SDK**, implementing the core tenets of the **Super Simple Product Factory (SSSF)** philosophy, expanded with advanced Platform Engineering standards.

---

## 🧬 Core Philosophy: Fusing Agno with SSSF

While **Agno** provides an incredible set of low-level agentic primitives (`Agents`, `Teams`, `Workflows`, `Tools`), it behaves as a blank canvas. **SSSF** provides a dogmatic set of constraints to prevent AI from failing unpredictably. 

**APF** bridges this gap, providing a robust, production-ready framework that ensures:

1. **Sovereignty of Code**: The execution graph is governed by deterministic Python code (`ApfWorkflow`), never by LLM cognition.
2. **Clear Lanes of Execution**: Tasks are strictly partitioned into `agent` (cognitive), `code` (deterministic/bash), and `engineer` (human-in-the-loop) lanes.
3. **Physical Contracts (JSON Envelopes)**: Handoffs between phases are done strictly through structured Pydantic-validated JSON files (`EnvelopeBase`).
4. **Post-Phase Gates**: Code assertions (linters, test suites, git diffs) verify the output of a phase before letting the pipeline progress.
5. **In-Session Correction Loops**: When a gate fails, the agent is re-prompted within its active session with structured error feedback, avoiding cold restarts.

---

## 🛠️ Tool Management & Least Privilege

Agents in APF are mathematically bounded by the tools they are assigned. A Planner cannot write files, and a Scout cannot execute bash commands. This is enforced natively through Agno Toolkits.

👉 **[Read the deep dive into Tool Management](docs/TOOL_MANAGEMENT.md)**

---

## 🧠 The 5-Layer Cognitive Topology

APF eliminates "Prompt Dilution" and "Handoff Amnesia" by dynamically injecting 5 decoupled layers of context into an agent at runtime:
1. **Identity:** Hardcoded archetype rules and physical Tool limits.
2. **Ecosystem:** The global repository rules loaded from `AI.md`.
3. **Original Intent:** The initial GitHub Issue, propagated to all downstream agents.
4. **Current State:** The structured Pydantic `Envelope` passed from the previous agent.
5. **Task-Specific Skills:** Modular methodologies (e.g., `conventional_commits`) injected on-demand.

👉 **[Read the deep dive into the Cognitive Topology](docs/COGNITIVE_TOPOLOGY.md)**

---

## 🌟 Key Features (v1.0)

### 🚀 1. The Inception Engine (`stamp.py`)
APF is deployed via "stamping". Run `uv run apf stamp` in your target repository.
- **Greenfield**: If the repo is empty, an interactive agent interviews you and generates industry-standard `catalog-info.yaml` and a high-density `AI.md` file.
- **Brownfield**: If the repo has code, the agent reads the `README.md` and deduces the context automatically.

### 🧠 2. The Universal Archetypes & 3-Tier Strategy
APF includes 6 immutable agent archetypes (`scout`, `planner`, `structurer`, `builder`, `reviewer`, `documenter`). 
Instead of hardcoding models, APF uses `apf.yaml` to map tasks to a **3-Tier Model Pool** (`heavy`, `workhorse`, `lightweight`). If a primary model fails, the engine automatically routes to the next fallback model.

### 🛡️ 3. Envelope Wrapper & Git Security
- **Universal Two-Step Harness**: To prevent complex models from hallucinating tool parameters when generating JSON, APF separates execution (free-form cognition with tools) from formatting (a lightweight agent extracting the Pydantic JSON).
- **Git Rollback Security**: The `security.py` module takes a Git snapshot before an agent runs. If the agent modifies files it wasn't authorized to touch, the phase fails and the repo is instantly reverted.

### 📊 4. Real-time SQLite Telemetry
Every lane execution and agent run is logged in real-time to a WAL-mode SQLite database (`.context/data/telemetry.db`), capturing duration, tokens, and model routing for dashboard integration.

### 🛠️ 5. Generative CLI (`apf-cli`)
Stop writing boilerplate. Use the CLI to scaffold your pipelines:
```bash
# Generate a new Mermaid diagram and its Python runner
uv run python -m apf_core.cli generate workflow deploy_fix --agents scout,builder,reviewer

# Generate a new Pydantic Envelope and Agno Agent class
uv run python -m apf_core.cli generate agent security_auditor
```

---

## ⚠️ System Prerequisites

Before stamping or running APF on a new machine or CI/CD pipeline, your host environment **MUST** have the following installed:
1. **Python 3.10+**
2. **[uv](https://docs.astral.sh/uv/)**: The ultra-fast Python package manager used for isolated execution.
3. **[GitHub CLI (gh)](https://cli.github.com/)**: Required for the GitOps Daemon to fetch issues and create PRs. You **must** be authenticated (`gh auth login`).

👉 **[Read the Prerequisites Guide for installation details](docs/PREREQUISITES.md)**

---

## 🛠️ Getting Started

### Installation
Run the following command inside your target repository to stamp the factory:
```bash
uv run https://raw.githubusercontent.com/saulfernandez-me/agno-product-factory/main/scripts/stamp.py --target .
```

### Next Steps
1. Rename `.env.example` to `.env` and configure your API keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`, etc.).
2. Review your generated `AI.md`.
3. Execute any of the 12 pre-built workflows located in the `workflows/` directory!

```bash
PYTHONPATH=src uv run python workflows/bug_fix_runner.py
```

---

## 📄 License

This project is open-source and licensed under the MIT License.
