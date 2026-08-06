from agno.agent import Agent
from pydantic import BaseModel

from asf_core.config import get_models_for_tier


def get_planner_agent(
    domain_context: str,
    task_instructions: str,
    output_schema: type[BaseModel],
    model_tier: str = "heavy",
) -> Agent:
    """
    Factory for the Planner Agent (The Strategic Orchestrator).

    Role:
        Decomposes feature requests into actionable, atomic technical steps.
        Does not execute or write implementation code.

    Capabilities:
        Pure cognition. No file writing tools.
    """

    return Agent(
        name="Planner",
        model=get_models_for_tier(model_tier)[0],
        fallback_models=get_models_for_tier(model_tier)[1:],  # type: ignore[arg-type]
        description="You are a Strategic Orchestrator. You decompose requests into actionable steps.",
        instructions=task_instructions,
        tools=[],  # Planners plan, they do not touch files.
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
        tool_call_limit=5,
    )
