from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


ReputationScope = Literal["seller", "buyer"]


class RatingCreate(BaseModel):
    reputation_scope: ReputationScope = Field(
        ...,
        description=(
            "'seller' = you are the buyer rating the seller. "
            "'buyer' = you are the seller rating the buyer."
        ),
    )
    stars: int = Field(..., ge=1, le=5, description="1–5 stars")
    comment: Optional[str] = Field(None, max_length=2000)


class RatingUpdate(BaseModel):
    """Identify the row with reputation_scope; send at least one of stars or comment."""

    reputation_scope: ReputationScope
    stars: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=2000)


class RatingOut(BaseModel):
    id: int
    listing_id: int
    from_user_id: int
    to_user_id: int
    reputation_scope: str
    stars: int
    comment: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RatingSummaryOut(BaseModel):
    """Separate aggregates: reputation as seller vs as buyer (from ratings received)."""

    as_seller_avg: Optional[float] = None
    as_seller_count: int = 0
    as_buyer_avg: Optional[float] = None
    as_buyer_count: int = 0
