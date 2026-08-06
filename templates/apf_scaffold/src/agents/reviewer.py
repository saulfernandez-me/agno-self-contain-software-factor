from pathlib import Path

from agno.agent import Agent
from pydantic import BaseModel

from apf_core.config import get_models_for_tier
from apf_core.tools.workspace_tools import (
    WorkspaceTools,  # type: ignore[import-not-found]
)


def get_reviewer_agent(
    domain_context: str,
    task_instructions: str,
    output_schema: type[BaseModel],
    model_tier: str = "heavy",
) -> Agent:
    """
    Factory for the Reviewer Agent (The Adversarial Auditor).
    """
    behavior_file = Path(".context/agents/reviewer_behavior.md")
    behavioral_harness = (
        behavior_file.read_text(encoding="utf-8")
        if behavior_file.exists()
        else "You are an Adversarial Auditor. You review code and look for flaws."
    )

    read_only_tools = WorkspaceTools(restrict_to_cwd=True)
    if hasattr(read_only_tools, "write_file"):
        delattr(read_only_tools, "write_file")

    return Agent(
        name="Reviewer",
        model=get_models_for_tier(model_tier)[0],
        fallback_models=get_models_for_tier(model_tier)[1:],  # type: ignore[arg-type]
        description=behavioral_harness,
        instructions=f"[DOMAIN CONTEXT & INVARIANTS]\n{domain_context}\n\n[TASK INSTRUCTIONS]\n{task_instructions}",
        tools=[read_only_tools],
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
        tool_call_limit=5,
    )
