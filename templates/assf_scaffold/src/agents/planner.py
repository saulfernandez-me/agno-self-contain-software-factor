from agno.agent import Agent
from pydantic import BaseModel


def get_planner_agent(
    domain_context: str,
    task_instructions: str,
    response_model: type[BaseModel],
    model_id: str = "openai:gpt-4o",
) -> Agent:
    """
    Factory for the Planner Agent (The Strategic Orchestrator).

    Role:
        Decomposes feature requests into actionable, atomic technical steps.
        Does not execute or write implementation code.

    Capabilities:
        Pure cognition. No file writing tools.
    """

    return Agent(
        name="Planner",
        model=model_id,
        description="You are a Strategic Orchestrator. You decompose requests into actionable steps.",
        instructions=task_instructions,
        tools=[],  # Planners plan, they do not touch files.
        response_model=response_model,  # type: ignore[call-arg]
        add_history_to_messages=True,  # type: ignore[call-arg]
    )
