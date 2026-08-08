# 🤖 APF Agent Archetypes

This directory contains the core cognitive workers of the **Agno Product Factory (APF)**. 

Instead of creating dozens of hyper-specific agents (e.g., `frontend_dev`, `database_admin`, `qa_engineer`), APF relies on **8 Universal Archetypes**. Their physical capabilities (Tools) and base cognitive power (Model Tiers) are hardcoded in these Python files, ensuring the **Principle of Least Privilege**.

Their actual task instructions and domain knowledge are injected at runtime by the Workflows (via `.context/agents/*_behavior.md` and `AI.md`), making them truly domain-agnostic.

---

## 📋 2. Functional Analyst (`functional_analyst.py`)
- **Role:** The Translator.
- **Purpose:** Bridges the gap between the Product Owner and the Planner. Translates business MVPs into strict functional system behaviors without dictating code architecture.
- **Tools:** None (Pure cognition).
- **Tier:** `heavy`


## 👑 1. Product Owner (`product_owner.py`)
- **Role:** The Business Visionary / Voice of the User.
- **Purpose:** Analyzes Epics, defends business value, prevents scope creep, and defines the Minimum Viable Product (MVP).
- **Tools:** None (Pure cognition).
- **Tier:** `heavy`

## 📐 3. Planner (`planner.py`)
- **Role:** The Strategic Orchestrator / Scrum Master.
- **Purpose:** Decomposes business requirements into actionable, atomic technical steps. Designs software architecture without writing implementation code.
- **Tools:** Read-only `WorkspaceTools` (can explore the codebase to plan, but cannot write).
- **Tier:** `heavy`

## 🔍 4. Scout (`scout.py`)
- **Role:** The Information Miner.
- **Purpose:** Gathers deep context, reads logs, navigates repository structures, and searches the web to eliminate LLM hallucinations before tasks begin.
- **Tools:** Read-only `WorkspaceTools`, `BraveSearchTools`.
- **Tier:** `lightweight`

## 🏗️ 5. Builder (`builder.py`)
- **Role:** The Execution Worker / Core Implementer.
- **Purpose:** Strictly follows the technical plans to write code, tests, and configuration files. It is the **only** cognitive agent authorized to freely mutate the codebase.
- **Tools:** Write-enabled `WorkspaceTools`.
- **Tier:** `heavy`

## 🛡️ 6. Reviewer (`reviewer.py`)
- **Role:** The Adversarial Auditor.
- **Purpose:** Reviews code diffs against the original plan and domain rules. Hunts for logic flaws, security vulnerabilities, and architectural drift. Returns actionable feedback to the Builder.
- **Tools:** Read-only `WorkspaceTools`.
- **Tier:** `heavy`

## 🗂️ 7. Structurer (`structurer.py`)
- **Role:** The Data Taxonomist.
- **Purpose:** Cleans, maps, and transforms unstructured data into rigid schemas. Crucial for ERP integrations and dataset normalization.
- **Tools:** None (In-memory data transformation).
- **Tier:** `workhorse`

## 📝 8. Documenter (`documenter.py`)
- **Role:** The Technical Writer.
- **Purpose:** Synthesizes completed work into human-readable documentation. Writes PR descriptions, updates READMEs, and drafts release notes.
- **Tools:** Write-enabled `WorkspaceTools` (intended for markdown/docs).
- **Tier:** `lightweight`
