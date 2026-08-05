# 🤖 Agno Self-Contain Software Factor (ASSF) 🏭✨

> **ASSF** is a rigid, reliable, and deterministic Software Factory framework built on top of the **Agno SDK**, implementing the core tenets of the **Super Simple Software Factory (SSSF)** philosophy.

---

## 🧬 Core Philosophy: Fusing Agno with SSSF

While **Agno** provides an incredible set of low-level agentic primitives (`Agents`, `Teams`, `Workflows`, `Tools`), it behaves as a blank canvas—leaving execution safety and orchestration up to the developer. 

**SSSF** is a dogmatic set of constraints designed to prevent AI agents from failing unpredictably. **ASSF** bridges this gap, providing a robust, production-ready framework that ensures:

1. **Sovereignty of Code**: The execution graph is governed by deterministic Python code, never by LLM cognition.
2. **Clear Lanes of Execution**: Tasks are strictly partitioned into `agent` (cognitive), `code` (deterministic), and `engineer` (human-in-the-loop) lanes.
3. **Physical Contracts (JSON Envelopes)**: Handoffs between phases are done strictly through structured Pydantic-validated JSON files (Envelopes), preventing context drift and conversational noise.
4. **Post-Phase Gates**: Code assertions (linters, test suites, existence checks) verify the output of a phase before letting the pipeline progress.
5. **In-Session Correction Loops**: When a gate fails, the agent is re-prompted within its active session with structured error feedback, avoiding cold restarts.

---

## 🏛️ Architectural Blueprint

The lifecycle of an ASSF phase follows a strict steel rail pipeline:

```
             ┌──────────────────────────────────────────────────┐
             │         DETERMINISTIC GRAPH (Python Code)        │
             └────────┬────────────────────────────────┬────────┘
                      │                                │
     ┌────────────────▼────────────────┐      ┌────────▼────────┐
     │  AGENT PHASE (Bounded Cognition)│      │    CODE PHASE   │
     └────────────────┬────────────────┘      │ (Linter/Tests)  │
                      │                       └────────┬────────┘
             ┌────────▼────────┐                       │
             │ ENVELOPE (JSON) │                       │
             └────────┬────────┘                       │
                      │                                │
             ┌────────▼────────┐                       │
             │   GATES (DoD)   ├───────────────────────┘
             └────────┬────────┘
                      │
            ┌─────────┴─────────┐
            │    Pass Gates?    │
            └────┬──────────┬───┘
                 │          │
             Yes │       No │ (Re-prompt In-Session)
                 │          └───────────┐
        ┌────────▼────────┐       ┌─────▼─────────────┐
        │   NEXT PHASE    │       │  CORRECTION LOOP  │
        └─────────────────┘       └───────────────────┘
```

---

## 📂 Repository Structure

```
agno-self-contain-software-factor/
├── README.md                           # This file
├── docs/                               # Conceptual documentation
│   ├── ARCHITECTURE.md                 # Technical design and pillars
│   └── FEATURES.md                     # Roadmap and specifications
├── assf/                               # Source code (coming soon)
│   ├── core/                           # Factory engines, base workflow and envelopes
│   ├── agents/                         # Custom Agno agents with bounded roles
│   ├── gates/                          # Built-in verification gates
│   └── cli.py                          # Factory entrypoint CLI
└── tests/                              # Unit and integration tests
```

---

## 🚦 Technical Roadmap

### Phase 1: Conceptual & Contract Design (Current)
- [x] Establish the SSSF / Agno philosophical alignment.
- [ ] Define `EnvelopeBase` and specialized Pydantic contracts for handoffs.
- [ ] Document core Gates and the assertion architecture.

### Phase 2: Core Implementation
- [ ] Build the `AssfWorkflow` class wrapping Agno's Workflow engine to enforce deterministic steps.
- [ ] Implement the `with phase(...)` context manager to log and track execution lanes.
- [ ] Create the in-session correction loop handler.

### Phase 3: Built-In Agents & Gates
- [ ] Implement a standard Software Engineer agent team.
- [ ] Build default verification gates: `LinterGate`, `TestRunnerGate`, `FileValidatorGate`.

---

## 🛠️ Getting Started

*(Detailed installation and configuration instructions will be added as the codebase is implemented).*

---

## 📄 License

This project is open-source and licensed under the MIT License.
