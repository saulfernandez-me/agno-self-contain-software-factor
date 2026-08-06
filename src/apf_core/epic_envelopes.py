from pydantic import BaseModel, Field

from apf_core.envelopes import EnvelopeBase


class ProductAnalysisEnvelope(EnvelopeBase):
    """
    Output contract for the Product Analysis phase (The 'Brain' / Reviewer acting as PO).
    """

    business_validity: str = Field(
        ...,
        description="Evaluation of the feature's business logic and technical feasibility.",
    )
    edge_cases: list[str] = Field(
        ...,
        description="Potential edge cases or security risks identified in the request.",
    )
    recommended_mvp_scope: str = Field(
        ...,
        description="The constrained, Minimum Viable Product scope recommended to build.",
    )


class GithubIssueSchema(BaseModel):
    """Schema for a single atomized GitHub issue."""

    title: str = Field(
        ...,
        description="The proposed issue title (e.g., 'feat: create auth endpoint').",
    )
    description: str = Field(
        ...,
        description="The Markdown body of the issue, strictly following the APF Feature Template.",
    )
    labels: list[str] = Field(default=["apf:backlog"], description="Labels to attach.")


class BacklogEnvelope(EnvelopeBase):
    """
    Output contract for the Breakdown phase (The Planner acting as Scrum Master).
    """

    issues: list[GithubIssueSchema] = Field(
        ..., description="The list of atomic GitHub Issues generated from the Epic."
    )
