---
name: apf
description: The Agno Self-Contain Software Factor (APF) super-skill. This skill contains the mandatory operational rules, architectural pillars, and routing tables for all agents working in an APF-stamped repository. Always consult this skill to understand how to write workflows, agents, and data envelopes.
---

# 🏭 APF: Agno Self-Contain Software Factor

> **CRITICAL DIRECTIVE:** You are operating inside an APF-stamped repository. You MUST adhere to these rules at all times. Failure to do so breaks the product factory.

## 1. 🌐 Hard Rules (Non-Negotiable)

1. **Strict English Boundary:** All source code, variables, commit messages, PRs, and documentation (`.md` files) MUST be written in English. Conversational chat with the user may be in their preferred language, but the repository artifacts are strictly English.
2. **Graph Sovereignty:** Do not attempt to write free-form agent loops. The workflow graph is owned by deterministic Python (`ApfWorkflow`). Agents are bounded nodes invoked by the Python code.
3. **Execution Lanes:** 
   - `kind="agent"`: LLM reasoning and file proposals.
   - `kind="code"`: Deterministic bash scripts, linters, and tests. Agents do NOT run linters themselves; the code lane does.
   - `kind="engineer"`: Human-in-the-loop approvals.
4. **Physical Contracts (Envelopes):** Never pass raw chat history to the next agent. You must output a JSON file conforming to a Pydantic `EnvelopeBase` model.
5. **Post-Phase Gates:** You are not "done" until local code assertions (tests, linters) pass. If they fail, you will receive an in-session correction prompt.

## 2. 📖 Routing Table (Cookbooks)

When asked to perform a specific APF task, refer to the following patterns (which will be defined in the `docs/` or `templates/` folder of this repository):

| Request | Action / Pattern to Follow |
| :--- | :--- |
| **"Create a new contract/envelope"** | Inherit from `EnvelopeBase` in `apf_core.envelopes`. Define strict Pydantic fields. |
| **"Create a new gate"** | Write a static Python function that returns `True/False` or raises an exception. It must check physical file state or command exit codes. |
| **"Create a workflow"** | Use Mermaid.js syntax to define the pipeline with `LANE: agent` and `LANE: code` subgraphs. |
| **"Run a workflow"** | Execute `uv run python <workflow_script.py>`. Never try to manually guess the next steps. |

## 3. 🧠 Agent Integration
By having this skill loaded, you inherently know how APF works. When reviewing code, generating Mermaid graphs, or writing Python for this repository, you must apply the 5 Pillars of APF described above.
