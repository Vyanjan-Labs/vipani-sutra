from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    poster = "poster"   # anyone who posts a listing
    admin = "admin"     # platform admin (you)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    city = Column(String, nullable=False)
    role = Column(String, default=UserRole.poster)
    shop_name = Column(String, nullable=True)   # optional — if they're a shop
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    listings = relationship("Listing", back_populates="owner")
