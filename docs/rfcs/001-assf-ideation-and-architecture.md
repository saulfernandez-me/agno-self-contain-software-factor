# RFC 001: Agno Self-Contain Software Factor (ASSF) - Ideation and Base Architecture

**Status:** Accepted
**Author:** Saúl Fernández (Platform Architect) / Tachikoma (Tech Lead)
**Date:** August 2026

---

## 1. The Problem (Origin of the Need)
In modern platform engineering, delegating complex development tasks to Artificial Intelligence agents (LLMs) presents a critical challenge: **non-determinism and the loss of Software Development Life Cycle (SDLC) control.**

1. **The SDK Trap (e.g., Agno):** Frameworks like Agno provide excellent primitives (`Agents`, `Workflows`, `Tools`) but act as a blank canvas. They do not dictate *how* agents should interact safely. This leads to architectures where the AI dynamically decides which step to execute next, resulting in infinite loops, tool hallucinations, and unpredictable token consumption.
2. **The Conversational Context Trap:** Passing massive chat histories between agents to share context degrades the model's attention and skyrockets costs.
3. **The Deployment Challenge (Portability):** Complex orchestration solutions usually live isolated in separate repositories, making it difficult for a product engineer to use the AI directly in their working repository quickly and without global configurations.

## 2. Ideation (Solution Synthesis)
To solve this, we devised **ASSF**. It is born from the need to merge our internal experience orchestrating `pi-subagents` with the dogmatic guidelines discovered in Dan Disler's **SSSF (Super Simple Software Factory)** framework.

Our ideation relies on three axioms:
* **If the LLM is probabilistic, the harness must be deterministic:** The AI proposes solutions, but Python code decides if they are approved and dictates the next step.
* **If AI is expensive, validation must be free:** Tests and linters (Gates) must run on the host machine at native speed, rather than asking the AI to read the console output.
* **If the framework is useful, it must be Stampable:** The solution must be capable of being injected (`stamp`) directly into any target repository, making it autonomous and executable via `uv`.

## 3. Architecture Proposal (The Pillars)
ASSF will be built as a **"Hybrid Library and Scaffold"** on top of the Agno SDK, strictly implementing:

1. **Graph Sovereignty (AssfWorkflow):** An engine where state transitions are pure Python code, not LLM decisions.
2. **Execution Lanes:** Strict separation between `agent` (cognition), `code` (local bash scripts), and `engineer` (human approval).
3. **Physical Contracts (Envelopes):** Agents communicate exclusively by reading and writing JSON files validated by `Pydantic`, eradicating the chat history as a method of data transfer.
4. **Post-Phase Validation Gates:** Static assertions that verify the success of a phase (file existence, passing tests) before advancing.
5. **In-Session Correction Loops:** If a Gate fails, the structured error is injected into the AI's active session for correction, bypassing the cost of a cold restart.

## 4. Proprietary Innovations over SSSF
Beyond applying the SSSF dogmas, ASSF introduces:
* **Bidirectional Visual Execution:** Using **Mermaid.js** not just as documentation, but as source code (a parser that converts Mermaid graphs into Python flows) and telemetry (live-generated traces).
* **Control Plane via GitHub Issues:** Templatizing Issues and state labels (`assf:planning`, `assf:implementing`) so that GitHub acts as the asynchronous control interface, replacing exclusive terminal interaction.
* **Visual Observability (Tachikoma Dash):** A local UI to financially audit token consumption and view the execution waterfall in real time.
