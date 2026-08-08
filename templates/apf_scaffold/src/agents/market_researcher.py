from pathlib import Path
from typing import Type

from agno.agent import Agent
from pydantic import BaseModel

from apf_core.config import get_models_for_tier
from agno.tools.bravesearch import BraveSearchTools

def get_market_researcher_agent(
    domain_context: str,
    task_instructions: str,
    output_schema: Type[BaseModel],
    model_tier: str = "heavy",
) -> Agent:
    """
    Factory for the Market Researcher Agent.
    """
    behavior_file = Path(".context/agents/market_researcher_behavior.md")
    behavioral_harness = (
        behavior_file.read_text(encoding="utf-8")
        if behavior_file.exists()
        else "You are a Market Researcher. Analyze market trends and competitor features."
    )

    return Agent(
        name="Market Researcher",
        model=get_models_for_tier(model_tier)[0],
        fallback_models=get_models_for_tier(model_tier)[1:],  # type: ignore[arg-type]
        description=behavioral_harness,
        instructions=f"[DOMAIN CONTEXT & INVARIANTS]\n{domain_context}\n\n[TASK INSTRUCTIONS]\n{task_instructions}",
        tools=[BraveSearchTools()],
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
        tool_call_limit=10,
    )
