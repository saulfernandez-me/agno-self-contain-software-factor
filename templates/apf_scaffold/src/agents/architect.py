from pathlib import Path
from typing import Type

from agno.agent import Agent
from pydantic import BaseModel

from apf_core.config import get_models_for_tier
from apf_core.tools.workspace_tools import WorkspaceTools  # type: ignore[import-not-found]


def get_architect_agent(
    domain_context: str,
    task_instructions: str,
    output_schema: Type[BaseModel],
    model_tier: str = "heavy",
) -> Agent:
    """
    Factory for the Architect Agent (The System Designer).
    """
    behavior_file = Path(".context/agents/architect_behavior.md")
    behavioral_harness = (
        behavior_file.read_text(encoding="utf-8")
        if behavior_file.exists()
        else "You are a Software Architect. You design systems and write Technical Specifications (RFCs)."
    )

    read_only_tools = WorkspaceTools(restrict_to_cwd=True)
    if "write_file" in read_only_tools.functions:
        del read_only_tools.functions["write_file"]

    return Agent(
        name="Architect",
        model=get_models_for_tier(model_tier)[0],
        fallback_models=get_models_for_tier(model_tier)[1:],  # type: ignore[arg-type]
        description=behavioral_harness,
        instructions=f"[DOMAIN CONTEXT & INVARIANTS]\n{domain_context}\n\n[TASK INSTRUCTIONS]\n{task_instructions}",
        tools=[read_only_tools],
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
        tool_call_limit=5,
    )
