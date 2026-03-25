from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.listing import Listing
from app.models.user import User
from app.schemas.user import UserOut
from app.schemas.listing import ListingOut

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current logged-in user profile."""
    return current_user

@router.get("/me/listings", response_model=List[ListingOut])
def get_my_listings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all listings posted by the current user."""
    return db.query(Listing).filter(
        Listing.user_id == current_user.id
    ).order_by(Listing.created_at.desc()).all()
