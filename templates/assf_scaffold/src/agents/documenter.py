from agno.agent import Agent
from agno.tools.file import FileTools
from pydantic import BaseModel

from assf_core.config import get_models_for_tier


def get_documenter_agent(
    domain_context: str,
    task_instructions: str,
    output_schema: type[BaseModel],
    model_tier: str = "lightweight",
) -> Agent:
    """
    Factory for the Documenter Agent (The Technical Writer).

    Role:
        Synthesizes completed work into human-readable documentation.
        Writes PR descriptions, updates READMEs, and drafts release notes.

    Capabilities:
        Write-enabled FileSystem (intended for markdown/docs).
    """

    return Agent(
        name="Documenter",
        model=get_models_for_tier(model_tier)[0],
        fallback_models=get_models_for_tier(model_tier)[1:],  # type: ignore[arg-type]
        description="You are a Technical Writer. You synthesize work into documentation.",
        instructions=task_instructions,
        tools=[FileTools(enable_read_file=True, enable_save_file=True)],
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
    )
