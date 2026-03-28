from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Rating(Base):
    """
    One row per rating on a sold listing.

    from_user_id — who submitted the stars (the rater).
    to_user_id   — who those stars are about (the person being scored).

    reputation_scope — which reputation line this updates for *to_user_id*:
      seller = stars count toward their trust as a seller on this deal.
      buyer  = stars count toward their trust as a buyer on this deal.

    Unique per (listing, from_user, scope): one rating per direction per listing.
    """

    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint(
            "listing_id",
            "from_user_id",
            "reputation_scope",
            name="uq_rating_listing_from_scope",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(
        Integer,
        ForeignKey("listings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reputation_scope = Column(String, nullable=False)
    stars = Column(SmallInteger, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    listing = relationship("Listing", back_populates="ratings")
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="ratings_given")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="ratings_received")
