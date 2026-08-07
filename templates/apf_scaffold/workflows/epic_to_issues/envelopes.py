from typing import Literal

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


class FunctionalRequirementsEnvelope(EnvelopeBase):
    """
    Output contract for the Functional Analyst.
    """

    user_flows: list[str] = Field(
        ...,
        description="Detailed step-by-step behaviors expected from the system.",
    )
    error_states: list[str] = Field(
        ...,
        description="How the system should handle edge cases specified by the PO.",
    )
    acceptance_criteria: list[str] = Field(
        ...,
        description="Strict, testable criteria the architecture must satisfy.",
    )


class GithubIssueSchema(BaseModel):
    """Schema for a single atomized GitHub issue."""

    title: str = Field(
        ...,
        description="The proposed issue title without the type prefix.",
    )
    issue_type: Literal["feature", "bug", "task"] = Field(
        ...,
        description="The categorization of the issue. 'feature' for new value, 'bug' for fixes, 'task' for technical chores.",
    )
    rfc_pointer: str = Field(
        ...,
        description="The exact relative path to the physical RFC document (e.g., 'docs/rfcs/001-feature-name.md').",
    )
    execution_task: list[str] = Field(
        ...,
        description="A highly detailed, step-by-step technical plan for this specific atomic task.",
    )
    definition_of_done: list[str] = Field(
        ...,
        description="Clear acceptance criteria checklists.",
    )
    verification_command: str = Field(
        default="uv run pytest",
        description="The exact bash command to verify this issue locally (e.g., 'uv run pytest tests/test_auth.py').",
    )
    lifecycle_label: str = Field(
        default="apf:backlog", description="The lifecycle state, must be 'apf:backlog'"
    )
    size_label: str = Field(
        ...,
        description="The estimated effort/complexity (e.g., 'size: S', 'size: M', 'size: L', 'size: XL')",
    )
    scope_label: str = Field(
        ...,
        description="The architectural boundary (e.g., 'scope: frontend', 'scope: backend', 'scope: infra')",
    )
    thematic_labels: list[str] = Field(
        default_factory=list,
        description="Flexible semantic tags (e.g., 'jwt', 'database', 'ui-rework').",
    )


class BacklogEnvelope(EnvelopeBase):
    """
    Output contract for the Breakdown phase.
    """

    epic_title: str = Field(
        ...,
        description="A concise, 3-5 word title summarizing the overall business Epic.",
    )
    rfc_content: str = Field(
        ...,
        description="The full Markdown content of the Request for Comments (Tech Spec) document outlining the entire architecture and logic.",
    )
    rfc_path: str = Field(
        ...,
        description="The relative path where the RFC should be saved (e.g., 'docs/rfcs/001-feature-name.md').",
    )
    issues: list[GithubIssueSchema] = Field(
        ..., description="The list of atomic GitHub Issues generated from the Epic."
    )
