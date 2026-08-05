from agno.agent import Agent
from agno.tools.file import FileTools
from pydantic import BaseModel


def get_reviewer_agent(
    domain_context: str,
    task_instructions: str,
    response_model: type[BaseModel],
    model_id: str = "openai:gpt-4o",
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
        model=model_id,
        description="You are an Adversarial Auditor. You review code and look for flaws.",
        instructions=task_instructions,
        tools=[FileTools(read_access=True, write_access=False)],
        response_model=response_model,  # type: ignore[call-arg]
        add_history_to_messages=True,  # type: ignore[call-arg]
    )
