from pathlib import Path

from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from pydantic import BaseModel

from apf_core.config import get_models_for_tier
from apf_core.tools.workspace_tools import (
    WorkspaceTools,  # type: ignore[import-not-found]
)


def get_scout_agent(
    domain_context: str,
    task_instructions: str,
    output_schema: type[BaseModel],
    model_tier: str = "lightweight",
) -> Agent:
    """
    Factory for the Scout Agent (The Information Miner).
    """
    behavior_file = Path(".context/agents/scout_behavior.md")
    behavioral_harness = (
        behavior_file.read_text(encoding="utf-8")
        if behavior_file.exists()
        else "You are an Information Miner. You gather context and verify facts."
    )

    return Agent(
        name="Scout",
        model=get_models_for_tier(model_tier)[0],
        fallback_models=get_models_for_tier(model_tier)[1:],  # type: ignore[arg-type]
        description=behavioral_harness,
        instructions=f"[DOMAIN CONTEXT & INVARIANTS]\n{domain_context}\n\n[TASK INSTRUCTIONS]\n{task_instructions}",
        tools=[
            WorkspaceTools(restrict_to_cwd=True),
            DuckDuckGoTools(),
        ],
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
        tool_call_limit=5,
    )
