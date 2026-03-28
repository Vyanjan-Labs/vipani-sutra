from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    firebase_uid = Column(String, unique=True, index=True, nullable=True)
    # City and street are optional for everyone (buyers and sellers); listings / settings can carry location later.
    city = Column(String, nullable=True)
    address = Column(Text, nullable=True)

    # Product roles: same person can buy, sell, or both (explorer defaults: buyer-only).
    is_buyer = Column(Boolean, default=True, nullable=False)
    is_seller = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    buyer_profile = relationship(
        "BuyerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    seller_profile = relationship(
        "SellerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan", 
    )
    listings = relationship("Listing", back_populates="owner")
    listings_as_buyer = relationship("Listing", back_populates="buyer")
    ratings_given = relationship("Rating", back_populates="from_user")
    ratings_received = relationship("Rating", back_populates="to_user")
