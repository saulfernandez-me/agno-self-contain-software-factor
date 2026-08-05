from agno.agent import Agent
from assf_core.tools.workspace_tools import WorkspaceTools # type: ignore[import-not-found]
from pydantic import BaseModel

from assf_core.config import get_models_for_tier


def get_reviewer_agent(
    domain_context: str,
    task_instructions: str,
    output_schema: type[BaseModel],
    model_tier: str = "heavy",
) -> Agent:
    """
    Factory for the Reviewer Agent (The Adversarial Auditor).

    Role:
        Reviews outputs (diffs) against plans and rules.
        Looks for logic flaws, security vulnerabilities, and architectural drift.

    Capabilities:
        Read-only FileSystem (cannot fix the code itself).
    """

    return Agent(
        name="Reviewer",
        model=get_models_for_tier(model_tier)[0],
        fallback_models=get_models_for_tier(model_tier)[1:],  # type: ignore[arg-type]
        description="You are an Adversarial Auditor. You review code and look for flaws.",
        instructions=task_instructions,
        tools=[WorkspaceTools(restrict_to_cwd=True)],
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
        tool_call_limit=5,
    )
