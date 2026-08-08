from typing import Literal

from pydantic import BaseModel, Field

from apf_core.envelopes import EnvelopeBase


class MarketResearchEnvelope(EnvelopeBase):
    """
    Output contract for the Market Researcher.
    """
    market_trends: list[str] = Field(
        ...,
        description="Key industry trends identified through research.",
    )
    competitor_gaps: list[str] = Field(
        ...,
        description="Weaknesses or missing features in competitor products.",
    )
    macro_opportunities: list[str] = Field(
        ...,
        description="High-level areas where the product could expand or improve.",
    )


class UXResearchEnvelope(EnvelopeBase):
    """
    Output contract for the User Advocate.
    """
    user_pain_points: list[str] = Field(
        ...,
        description="Specific frictions or problems faced by the target user personas.",
    )
    unmet_needs: list[str] = Field(
        ...,
        description="Features or capabilities users want but do not have.",
    )
    ux_opportunities: list[str] = Field(
        ...,
        description="How the market trends can solve specific user pain points.",
    )


class OpportunitySchema(BaseModel):
    """Schema for a single Opportunity Epic."""
    title: str = Field(
        ...,
        description="A clear, concise title for the Epic opportunity.",
    )
    problem_statement: str = Field(
        ...,
        description="The core problem this opportunity aims to solve for the user.",
    )
    potential_value_roi: str = Field(
        ...,
        description="The expected business value or return on investment (ROI).",
    )
    target_audience: str = Field(
        ...,
        description="The specific user persona or segment this benefits.",
    )
    epic_size: Literal["size: S", "size: M", "size: L", "size: XL"] = Field(
        ...,
        description="T-Shirt size estimation for the overall effort of the Epic.",
    )
    thematic_labels: list[str] = Field(
        default_factory=list,
        description="Flexible semantic tags (e.g., 'ai', 'ux', 'database').",
    )


class ProductDiscoveryEnvelope(EnvelopeBase):
    """
    Output contract for the Product Strategist.
    """
    strategic_summary: str = Field(
        ...,
        description="A high-level summary of the discovered opportunities and the rationale behind them.",
    )
    opportunities: list[OpportunitySchema] = Field(
        ...,
        description="A list of 1 to 3 high-ROI opportunity proposals.",
    )
