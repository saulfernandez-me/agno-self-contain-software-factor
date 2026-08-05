from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.file import FileTools
from pydantic import BaseModel


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
        model=model_tier,  # type: ignore[arg-type]
        description="You are an Information Miner. You gather context and verify facts.",
        instructions=task_instructions,
        tools=[FileTools(enable_read_file=True, enable_save_file=False), DuckDuckGoTools()],
        output_schema=output_schema,  # type: ignore[call-arg]
        add_history_to_context=True,  # type: ignore[call-arg]
    )
