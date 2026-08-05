from agno.agent import Agent
from pydantic import BaseModel

from assf_core.config import get_models_for_tier


def get_structurer_agent(
    domain_context: str,
    task_instructions: str,
    output_schema: type[BaseModel],
    model_tier: str = "workhorse",
) -> Agent:
    """
    Factory for the Structurer Agent (The Data Taxonomist).

    Role:
        Cleans, maps, and transforms unstructured data into rigid schemas.
        Crucial for ERP integrations, catalog mapping, and data normalization.

    Capabilities:
        Pure cognition (schema mapping). No file tools.
    """

    return Agent(
        name="Structurer",
        model=get_models_for_tier(model_tier)[0],
        fallback_models=get_models_for_tier(model_tier)[1:],  # type: ignore[arg-type]
        description="You are a Data Taxonomist. You clean and map unstructured data.",
        instructions=task_instructions,
        tools=[],  # Data mapping is typically an input-output operation in memory
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
    )
