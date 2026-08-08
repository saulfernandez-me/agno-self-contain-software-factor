from pathlib import Path
from typing import Type

from agno.agent import Agent
from pydantic import BaseModel

from apf_core.config import get_models_for_tier


def get_user_advocate_agent(
    domain_context: str,
    task_instructions: str,
    output_schema: Type[BaseModel],
    model_tier: str = "heavy",
) -> Agent:
    """
    Factory for the User Advocate Agent.
    """
    behavior_file = Path(".context/agents/user_advocate_behavior.md")
    behavioral_harness = (
        behavior_file.read_text(encoding="utf-8")
        if behavior_file.exists()
        else "You are a User Advocate. Identify UX frictions and unmet user needs."
    )

    return Agent(
        name="User Advocate",
        model=get_models_for_tier(model_tier)[0],
        fallback_models=get_models_for_tier(model_tier)[1:],  # type: ignore[arg-type]
        description=behavioral_harness,
        instructions=f"[DOMAIN CONTEXT & INVARIANTS]\n{domain_context}\n\n[TASK INSTRUCTIONS]\n{task_instructions}",
        tools=[],
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
        tool_call_limit=5,
    )
