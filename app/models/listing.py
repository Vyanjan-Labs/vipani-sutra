from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, ARRAY, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

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
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="listings")
