# 🏗️ Structure and Deployment (Stamping)

This document outlines the physical directory structure of **APF**, how it is packaged, and how it is deployed (stamped) into target repositories.

---

## 1. The SSSF Inspiration: The "Stamping" Paradigm

In Dan Disler's SSSF, the framework is not a traditional dependency (like an npm package or pip library) that hides its logic in `node_modules` or `site-packages`. Instead, it uses a **"stamping"** approach.

*   **How SSSF works**: You download the factory as a "skill" into a `.claude/skills/sssf/` folder. You run an `install.py` script. The script physically copies (`stamps`) the workflow scripts (`adws/`), the prompts, and the configs directly into your repository.
*   **Why?**: By placing the orchestration code (the graph) directly in your repository, you have complete ownership. You can modify the Python workflow scripts, tweak the gates, and adjust the prompts without fighting a rigid third-party library.

---

## 2. Our APF Approach: The Hybrid "Library + Scaffold" Model

For APF, because we are building on top of the **Agno SDK** and integrating with our own `pi-coding-agent` ecosystem, we will adopt a **Hybrid Model**:

1.  **The Core Engine (Library)**: The heavy lifting—base classes like `ApfWorkflow`, `EnvelopeBase`, and the telemetry/SQLite engine—will live in an installable Python package (`apf-core`). This ensures bug fixes to the engine benefit all repositories without manual copy-pasting.
2.  **The Stamped Factory (Scaffold)**: The actual workflows (the graphs), the agent definitions, the gates, and the prompts will be **stamped** (copied) into the target repository. This gives the developer full control over the PDLC of that specific project.

### The APF Repository Structure (Framework Development)

This repository (`saulfernandez-me/agno-product-factory`) is where we build the framework itself.

```
agno-product-factory/
├── README.md
├── docs/                       # Architectural documentation
├── src/
│   └── apf_core/              # The pip-installable python package
│       ├── envelopes.py        # EnvelopeBase definition
│       ├── gates.py            # Base gate runner logic
│       ├── workflow.py         # ApfWorkflow extending Agno Workflow
│       └── telemetry/          # SQLite tracing and observability
├── templates/                  # The files that get stamped into a target repo
│   ├── apf_workflows/         # Deterministic workflow scripts
│   ├── agents/                 # Default Agno agents (Scout, Builder, Reviewer)
│   ├── gates/                  # Customizable assertion scripts
│   ├── prompts/                # System and user prompts in Markdown
│   └── apf.config.yaml        # Factory configuration
├── scripts/
│   └── stamp.py                # The CLI script to inject the factory into a repo
└── tests/                      # Framework tests
```

---

## 3. How a Target Repository Uses APF

When a developer wants to use APF in a new project (e.g., `lmdi-backend`), they will run the stamping script.

```bash
uv run https://raw.githubusercontent.com/saulfernandez-me/agno-product-factory/main/scripts/stamp.py
```

This will inject the **Scaffold** into the target repository:

```
lmdi-backend/ (Target Repo)
├── src/                        # The project's actual code
├── tests/                      # The project's tests
├── .context/                      # The stamped APF Factory
│   ├── workflows/              # e.g., build_and_test.py, research_feature.py
│   ├── agents/                 # The Agno agents tailored for this repo
│   ├── gates/                  # The specific acceptance criteria for this repo
│   ├── prompts/                # Prompts for this repo's context
│   ├── data/                   # The local SQLite trace DB and envelope JSONs
│   └── config.yaml             # Roster and model definitions
└── justfile                    # Recipes to run the factory (e.g., `just build`)
```

### The Execution Flow in the Target Repo

1.  **Invocation**: The developer (or a CI pipeline) triggers a workflow: `uv run .context/workflows/build_and_test.py "Add a new API endpoint for user login"`.
2.  **Lane 1 (Agent)**: The workflow instantiates the Builder Agent, passes the prompt, and gets a `BuildEnvelope` JSON back.
3.  **Lane 2 (Code)**: The workflow runs the local gates (e.g., `ruff check`, `pytest`).
4.  **Correction Loop**: If tests fail, the workflow re-prompts the Builder Agent in the same session with the stderr output.
5.  **Completion**: The final output is written, and telemetry is saved in `.context/data/telemetry.db`.
