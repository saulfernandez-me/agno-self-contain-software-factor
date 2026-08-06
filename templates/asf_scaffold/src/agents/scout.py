from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from pydantic import BaseModel

from asf_core.config import get_models_for_tier
from asf_core.tools.workspace_tools import (
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

    Role:
        Gathers context, reads the codebase, performs web research.
        Does not analyze deeply or plan. Reports raw facts.

    Capabilities:
        Read-only FileSystem, Web Search.
    """

    return Agent(
        name="Scout",
        model=get_models_for_tier(model_tier)[0],
        fallback_models=get_models_for_tier(model_tier)[1:],  # type: ignore[arg-type]
        description="You are an Information Miner. You gather context and verify facts.",
        instructions=task_instructions,
        tools=[
            WorkspaceTools(restrict_to_cwd=True),
            DuckDuckGoTools(),
        ],
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
        tool_call_limit=5,
    )
