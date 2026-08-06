# Cookbook 02: Creating an Agno Agent for APF

> **Purpose:** This guide dictates how to instantiate and configure an Agno `Agent` so it complies with the strict physical contract boundaries (Pydantic Envelopes) of APF.

## 1. The Agno Agent Configuration

When creating a new agent in `src/agents/`, you must construct a standard Agno `Agent` but force it to output structured data.

### Rules for the Agent:
1. **Model Agnostic:** The LLM provider (OpenAI, Anthropic, Gemini) should be configurable via `apf.yaml`, not hardcoded.
2. **`output_schema`:** You MUST set the `output_schema` argument to a subclass of `EnvelopeBase`. The agent cannot return plain text.
3. **Session Persistence:** Ensure `session_id` is maintained so correction loops do not trigger a cold start.

### Example: `src/agents/planner.py`
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from apf_core.envelopes import EnvelopeBase
from pydantic import Field
from typing import List


# 1. Define the specific Envelope for this phase
class PlannerEnvelope(EnvelopeBase):
    """The physical contract output of the Planner agent."""

    architectural_decisions: List[str] = Field(
        ..., description="Key technical decisions."
    )
    target_files: List[str] = Field(..., description="Files to be created or modified.")


# 2. Instantiate the Agno Agent
def get_planner_agent(session_id: str | None = None) -> Agent:
    return Agent(
        name="Planner",
        model=OpenAIChat(id="gpt-4o"),  # In production, read from apf.yaml
        description="You are a senior software architect.",
        instructions="Analyze the feature request and emit a technical plan. You do not write code.",
        output_schema=PlannerEnvelope,  # MANDATORY in APF
        session_id=session_id,
        add_history_to_context=True,  # Critical for In-Session Correction Loops
    )
```

## 2. Using the Agent in a Workflow

The orchestration runner handles the execution. Because the `output_schema` is set, Agno guarantees that the `response.data` property will contain a fully validated Pydantic object, which serves as the physical contract for the next phase.
