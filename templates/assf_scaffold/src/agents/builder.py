from agno.agent import Agent

# Note: In production, these tool imports might change depending on the specific agno tools available.
# We assume standard FileTools exist or can be built.
from agno.tools.file import FileTools
from pydantic import BaseModel


def get_builder_agent(
    domain_context: str,
    task_instructions: str,
    response_model: type[BaseModel],
    model_id: str = "openai:gpt-4o",  # Default, ideally injected from yaml
) -> Agent:
    """
    Factory for the Builder Agent (The Execution Worker).

    Role:
        Strictly follows plans. Writes code, tests, or configurations.
        Does not architect or second-guess the design.

    Capabilities:
        Write-enabled FileSystem.
    """

    return Agent(
        name="Builder",
        model=model_id,
        description="You are the Execution Worker. You strictly implement plans and write code to disk.",
        instructions=task_instructions,
        tools=[FileTools(read_access=True, write_access=True)],
        response_model=response_model,  # type: ignore[call-arg]
        add_history_to_messages=True,  # type: ignore[call-arg]
    )
