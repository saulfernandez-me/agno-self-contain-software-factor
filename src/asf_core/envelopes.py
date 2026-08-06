from typing import Any, Literal

from pydantic import BaseModel, Field


class EnvelopeBase(BaseModel):
    """
    Base contract for all physical data handoffs between agents in ASF.
    Replaces informal chat communication with rigid, Pydantic-validated JSON schemas.
    """

    status: Literal["success", "fail"] = Field(
        ..., description="Execution status of the phase."
    )
    summary: str = Field(
        ..., description="A short summary of what this phase achieved."
    )
    artifacts: list[str] = Field(
        default_factory=list,
        description="List of physical file paths created or edited during the phase.",
    )
    notes_for_next_agent: str = Field(
        ..., description="Direct technical instructions for the subsequent node."
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Execution and token metrics (e.g., duration, cost).",
    )


class BuildEnvelope(EnvelopeBase):
    """
    Example schema representing the output of a Builder agent phase.
    """

    commit_message: str = Field(
        default="", description="Suggested commit message for these changes."
    )


class ResearchEnvelope(EnvelopeBase):
    """
    Example schema representing the output of a Research or Scout agent phase.
    """

    sources_consulted: list[str] = Field(
        default_factory=list,
        description="List of URLs or paths consulted during research.",
    )
