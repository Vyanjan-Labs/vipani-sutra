from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_admin_user
from app.models.listing import Listing
from app.models.user import User
from app.schemas.listing import ListingOut
from app.schemas.user import UserOut

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/listings", response_model=List[ListingOut])
def get_all_listings(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Admin: see all listings including removed ones."""
    return db.query(Listing).order_by(Listing.created_at.desc()).all()

@router.patch("/listings/{listing_id}/remove")
def remove_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Admin: remove a bad or spam listing."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    listing.status = "removed"
    db.commit()
    return {"message": "Listing removed"}

@router.get("/users", response_model=List[UserOut])
def get_all_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_admin_user)
):
    """Admin: see all registered users."""
    return db.query(User).order_by(User.created_at.desc()).all()
