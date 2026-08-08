from typing import Literal

from pydantic import BaseModel, Field

from apf_core.envelopes import EnvelopeBase


class OpportunityAnalysisEnvelope(EnvelopeBase):
    """
    Output contract for the Product Owner refining an Opportunity.
    """
    business_validity: str = Field(
        ...,
        description="Evaluation of the opportunity's business logic and technical feasibility.",
    )
    recommended_mvp_scope: str = Field(
        ...,
        description="The constrained, Minimum Viable Product scope recommended to build.",
    )
    target_lifecycle_phase: Literal["MVP", "SCALE", "REFACTOR_TECH_DEBT"] = Field(
        ...,
        description="Determine the lifecycle phase based on the Epic's tags or intent.",
    )
    epic_title: str = Field(
        ...,
        description="A concise, 3-5 word title summarizing the overall business Epic.",
    )


class BusinessMetricsEnvelope(EnvelopeBase):
    """
    Output contract for the Business Analyst.
    """
    kpis: list[str] = Field(
        ...,
        description="1-3 Key Performance Indicators (KPIs) to measure success.",
    )
    data_requirements: list[str] = Field(
        ...,
        description="What telemetry or tracking needs to be built to measure the KPIs.",
    )


class TechSanityCheckEnvelope(EnvelopeBase):
    """
    Output contract for the Tech Lead.
    """
    is_feasible: bool = Field(
        ...,
        description="True if the Epic is viable, False if it fundamentally breaks architectural invariants.",
    )
    architectural_guardrails: list[str] = Field(
        ...,
        description="High-level technical rules or warnings the Architect must follow.",
    )
    security_risks: list[str] = Field(
        ...,
        description="Potential security or performance risks to mitigate.",
    )


class EpicFormattingEnvelope(EnvelopeBase):
    """
    Output contract for the Scrum Master to format the final Epic document.
    """
    epic_markdown_path: str = Field(
        ...,
        description="The relative path where the Epic document was saved (e.g., 'docs/epics/EPIC-001.md'). MUST USE save_artifact tool.",
    )
