from pathlib import Path

from agno.agent import Agent
from pydantic import BaseModel

from apf_core.config import get_models_for_tier


def get_planner_agent(
    domain_context: str,
    task_instructions: str,
    output_schema: type[BaseModel],
    model_tier: str = "heavy",
) -> Agent:
    """
    Factory for the Planner Agent (The Strategic Orchestrator).
    """
    behavior_file = Path(".context/agents/planner_behavior.md")
    behavioral_harness = (
        behavior_file.read_text(encoding="utf-8")
        if behavior_file.exists()
        else "You are a Strategic Orchestrator. You decompose requests into actionable steps."
    )

    return Agent(
        name="Planner",
        model=get_models_for_tier(model_tier)[0],
        fallback_models=get_models_for_tier(model_tier)[1:],  # type: ignore[arg-type]
        description=behavioral_harness,
        instructions=f"[DOMAIN CONTEXT & INVARIANTS]\n{domain_context}\n\n[TASK INSTRUCTIONS]\n{task_instructions}",
        tools=[],  # Planners plan, they do not touch files.
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
        tool_call_limit=5,
    )
