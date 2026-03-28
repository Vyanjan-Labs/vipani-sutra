from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, ARRAY, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    buyer_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)       # Sports, Clothes, Electronics, etc.
    price = Column(Float, nullable=True)            # discounted price
    original_price = Column(Float, nullable=True)   # original MRP (optional)
    images = Column(ARRAY(String), default=[])      # cloudinary URLs
    city = Column(String, nullable=False)
    locality = Column(String, nullable=True)        # sector, colony etc.
    contact_number = Column(String, nullable=False)
    status = Column(String, default="active")       # active | sold | removed

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", foreign_keys=[user_id], back_populates="listings")
    buyer = relationship("User", foreign_keys=[buyer_user_id], back_populates="listings_as_buyer")
    ratings = relationship("Rating", back_populates="listing", cascade="all, delete-orphan")
