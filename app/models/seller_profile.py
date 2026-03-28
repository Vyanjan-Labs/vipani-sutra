from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SellerProfile(Base):
    """Seller KYC, shop identity, and trust — one row per user who sells."""

    __tablename__ = "seller_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    shop_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    # male | female | other | prefer_not_to_say
    sex = Column(String, nullable=True)
    # Values: none | pending | verified | rejected
    verification_status = Column(String, default="none", nullable=False)
    pan_number = Column(String, nullable=True)
    aadhaar_number = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="seller_profile")
