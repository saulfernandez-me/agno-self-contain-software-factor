# 🧠 The 5-Layer Cognitive Topology

In standard agentic frameworks, context is often passed as a single, massive "System Prompt" containing the persona, the repository rules, the coding standards, and the task. This leads to **Prompt Dilution**: the LLM suffers from attention fatigue and begins to hallucinate or ignore critical constraints.

**Agno Product Factory (APF)** solves this through the **5-Layer Cognitive Topology**. Instead of one monolithic prompt, the Python `ApfWorkflow` orchestrator dynamically assembles the agent's mind at runtime by injecting 5 decoupled layers of context precisely when needed.

---

## 🥞 The 5 Layers of Context

### Layer 1: Identity (The Archetype)
- **Question Answered:** *"Who am I and what are my physical limits?"*
- **Source:** Hardcoded in Python (`src/agents/*.py`) and `*_behavior.md`.
- **Mechanism:** Defines the base Agno `Agent`. It dictates the rigid behavioral harness (e.g., "You are a Builder, you never delete tests") and physically bounds the agent by assigning strict `Tools` (e.g., `WorkspaceTools` with write access). 

### Layer 2: Ecosystem (Domain Context)
- **Question Answered:** *"Where am I operating and what are the global laws?"*
- **Source:** The `AI.md` (or `CLAUDE.md`) file located at the root of the target repository.
- **Mechanism:** Injected as the `domain_context`. It defines the Tech Stack, Architectural Invariants (e.g., "No ORMs allowed"), and the Anti-Goals of the business product.

### Layer 3: Original Intent (The Mission)
- **Question Answered:** *"What did the human actually ask for at the very beginning?"*
- **Source:** The original GitHub Issue body, passed as the `task` parameter through the workflow.
- **Mechanism:** Injected into downstream agents (like the Reviewer or Documenter) to cure **Handoff Amnesia**. It ensures the final code is audited against the original business need, not just checking if it compiles.

### Layer 4: Current State (The Handoff Contract)
- **Question Answered:** *"What did the previous agent do, and what must I do right now?"*
- **Source:** The Pydantic `EnvelopeBase` (e.g., `PlanEnvelope`) returned by the preceding workflow step.
- **Mechanism:** A structured JSON object containing exact file paths, architectural decisions, and specific notes (`notes_for_next_agent`). It eliminates heuristics by providing mathematical exactness.

### Layer 5: Task-Specific Skills (Methodology)
- **Question Answered:** *"What expert techniques must I use to execute this specific task?"*
- **Source:** Markdown files in `.context/skills/` (e.g., `python_expert.md`, `conventional_commits.md`).
- **Mechanism:** Injected on-demand via the `skills=["..."]` argument in `wf.run_agent()`. Instead of polluting the global `AI.md` with git commit rules, the workflow injects the `conventional_commits` skill *only* when the Documenter is about to write the PR.

---

## 🏗️ Example: Assembling the Builder's Mind

When the `12_full_pdlc` workflow invokes the **Builder** agent, here is how the 5 layers are stacked in memory by the `ApfWorkflow` engine:

```text
======================================================================
[LAYER 1: IDENTITY] (From .context/agents/builder_behavior.md)
You are the Execution Worker (Builder). 
Your job is to strictly implement the provided plan...
NEVER modify the test file simply to make the test pass...
======================================================================
[LAYER 2: ECOSYSTEM] (From AI.md)
Tech Stack: Python 3.10, FastAPI.
Invariants: All data models must use Pydantic v2.
======================================================================
[LAYER 3: ORIGINAL INTENT] (From GitHub Issue)
User Story: As a user, I want a secure JWT login endpoint...
======================================================================
[LAYER 4: CURRENT STATE] (From Planner's Envelope)
[TECHNICAL INSTRUCTIONS FROM PLANNER]
Implement `login_route` in `src/api/auth.py`. 
Use the `jose` library for JWT signing.
======================================================================
[LAYER 5: SKILLS] (From .context/skills/python_expert.md)
[INJECTED SKILLS & METHODOLOGIES]
Type Safety: Every function signature must be strictly typed.
Exception Handling: Do not catch broad `Exception`.
======================================================================
```

By keeping these 5 layers modular, APF guarantees that an agent behaves with the precision of a Staff Engineer, adapting instantly whether it's deployed in a Software codebase or an Agroforestry design repository.
