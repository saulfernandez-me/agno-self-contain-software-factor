# 🏭 APF Workflows Catalog

This directory contains the core operational pipelines (Workflows) for the **Agno Product Factory (APF)**. 

Each workflow represents a distinct "assembly line" designed for a specific Product Development Lifecycle (PDLC) task. They are constructed using the **Dual-Engine Pattern**: a visual Mermaid graph (`.mermaid`) defining the logic, and a deterministic Python runner (`_runner.py`) executing it.

---

## 📑 Workflow Index

| Workflow ID | Name | Primary Use Case | Active Agents | Lanes Utilized |
| :--- | :--- | :--- | :--- | :--- |
| **01** | `generic_prompt` | Quick single-shot tasks without validation. | Builder | Agent |
| **02** | `recon_only` | Repository mapping and context extraction. | Scout | Agent |
| **03** | `plan_only` | Architectural design and task breakdown. | Planner | Agent |
| **04** | `build_only` | Pure execution from a pre-existing plan. | Builder | Agent |
| **05** | `quality_gates` | Fast linting and testing without AI tokens. | *None* | Code |
| **06** | `plan_build` | Two-step implementation (No automated tests). | Planner, Builder | Agent |
| **07** | `build_test` | Implementation with automated correction loop. | Builder | Agent, Code |
| **08** | `build_review` | Implementation with adversarial AI auditing. | Builder, Reviewer | Agent |
| **09** | `plan_build_test` | Standard 3-step feature implementation. | Planner, Builder | Agent, Code |
| **10** | `plan_build_test_quality`| Strict feature implementation (Lint + Test gates).| Planner, Builder | Agent, Code |
| **11** | `document_changes` | Auto-generate PRs and READMEs from git diffs. | Documenter | Agent, Code |
| **12** | `full_pdlc` | **The Golden Path:** End-to-end feature delivery. | Planner, Builder, Reviewer, Documenter | Agent, Code, HITL |
| **N/A** | `bug_fix` | Surgical operation to reproduce and fix a bug. | Scout, Builder | Agent, Code |
| **N/A** | `epic_to_issues` | **The Brain:** Decompose Epics into GitHub Issues.| Reviewer, Planner | Agent, Code |

---

## 🔬 Detailed Workflow Anatomy

*(For technical details on how to invoke these workflows from the APF Daemon, see the global architectural guidelines).*

### generic_prompt
A raw execution pipeline. The `Builder` is invoked directly with a user prompt. No verification is performed. Ideal for quick boilerplate generation.

### recon_only
A pure read-only pipeline. The `Scout` agent maps the repository or searches the web to build context. Impossible to modify files due to tool restrictions.

### plan_only
The architectural pipeline. The `Planner` agent reads the task and outputs a `PlanEnvelope` without writing any implementation code.

### build_only
The execution pipeline. The `Builder` assumes a plan already exists in the context and focuses entirely on mutating source files.

### quality_gates
The fastest pipeline. Skips the `agent` lane entirely and executes `ruff check` and `pytest` in the `code` lane to verify repository health at zero token cost.

### plan_build
A chained cognitive pipeline. The `Planner` designs the solution, and its output envelope is piped directly into the `Builder`. Lacks automated verification.

### build_test
The fundamental iterative loop. The `Builder` writes code, and the pipeline immediately jumps to the `code` lane to run tests. If tests fail, the `stderr` is fed back to the `Builder` in an **In-Session Correction Loop**.

### build_review
The cognitive auditing loop. Instead of relying on bash tests, the `Reviewer` agent acts as the gate, analyzing the diff for logic flaws. If the Reviewer rejects the code, the Builder is re-prompted.

### plan_build_test
The standard agile pipeline. Combines the architectural safety of the `Planner` with the deterministic verification of the `build_test` correction loop.

### plan_build_test_quality
The strict enterprise pipeline. Identical to `09`, but the `Builder` must pass a static linter (`ruff`) gate before the test suite (`pytest`) gate is even executed, saving test runner execution time on syntax errors.

### document_changes
The release pipeline. Uses the `code` lane to execute `git diff main`, pipes the physical diff to the `Documenter` agent, and outputs a formatted changelog or PR description.

### full_pdlc
**The comprehensive Product Development Lifecycle.** This is the default workflow used by the GitOps Daemon. 
*Flow: Planner (Designs) -> Builder (Writes) -> Code Gate (Tests & Loop) -> Reviewer (Audits & Loop) -> Documenter (PR Description).*

### bug_fix
A specialized surgical pipeline. The `Scout` is first deployed to reproduce the bug by gathering logs. Its context is fed to the `Builder`, followed by a strict test verification loop.

### epic_to_issues (The Brain)
The Product Management pipeline. The `Reviewer` acts as a Product Owner to define MVP scope and edge cases. The `Planner` acts as a Scrum Master to atomize the scope into technical tasks. Finally, the `code` lane uses the GitHub CLI to autonomously populate the project backlog.
