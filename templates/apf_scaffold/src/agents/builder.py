from pathlib import Path

from agno.agent import Agent
from pydantic import BaseModel

from apf_core.config import get_models_for_tier

# Note: In production, these tool imports might change depending on the specific agno tools available.
# We assume standard FileTools exist or can be built.
from apf_core.tools.workspace_tools import (
    WorkspaceTools,  # type: ignore[import-not-found]
)


def get_builder_agent(
    domain_context: str,
    task_instructions: str,
    output_schema: type[BaseModel],
    model_tier: str = "heavy",  # Default, ideally injected from yaml
) -> Agent:
    """
    Factory for the Builder Agent (The Execution Worker).
    """
    behavior_file = Path(".context/agents/builder_behavior.md")
    behavioral_harness = (
        behavior_file.read_text(encoding="utf-8")
        if behavior_file.exists()
        else "You are the Execution Worker. You strictly implement plans and write code to disk."
    )

    return Agent(
        name="Builder",
        model=get_models_for_tier(model_tier)[0],
        fallback_models=get_models_for_tier(model_tier)[1:],  # type: ignore[arg-type]
        description=behavioral_harness,
        instructions=f"[DOMAIN CONTEXT & INVARIANTS]\n{domain_context}\n\n[TASK INSTRUCTIONS]\n{task_instructions}",
        tools=[WorkspaceTools(restrict_to_cwd=True)],
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
        tool_call_limit=5,
    )
