from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.file import FileTools
from pydantic import BaseModel


def get_scout_agent(
    domain_context: str,
    task_instructions: str,
    response_model: type[BaseModel],
    model_id: str = "google:gemini-1.5-flash",
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
        model=model_id,
        description="You are an Information Miner. You gather context and verify facts.",
        instructions=task_instructions,
        tools=[FileTools(read_access=True, write_access=False), DuckDuckGoTools()],
        response_model=response_model,  # type: ignore[call-arg]
        add_history_to_messages=True,  # type: ignore[call-arg]
    )
