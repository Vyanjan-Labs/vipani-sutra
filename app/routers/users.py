from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.listing import Listing
from app.models.seller_profile import SellerProfile
from app.models.user import User
from app.schemas.user import SellerVerificationSubmit, UserOut
from app.schemas.listing import ListingOut
from app.schemas.rating import RatingSummaryOut
from app.services.rating_aggregate import rating_summary_for_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current logged-in user profile."""
    return current_user

@router.get("/me/rating-summary", response_model=RatingSummaryOut)
def get_my_rating_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Average rating received as seller vs as buyer (separate aggregates)."""
    return RatingSummaryOut(**rating_summary_for_user(db, current_user.id))


@router.get("/{user_id}/rating-summary", response_model=RatingSummaryOut)
def get_user_rating_summary(user_id: int, db: Session = Depends(get_db)):
    """Public rating summary for a user."""
    if not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="User not found")
    return RatingSummaryOut(**rating_summary_for_user(db, user_id))


@router.get("/me/listings", response_model=List[ListingOut])
def get_my_listings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all listings posted by the current user."""
    return db.query(Listing).filter(
        Listing.user_id == current_user.id
    ).order_by(Listing.created_at.desc()).all()


@router.post("/me/seller-verification", response_model=UserOut)
def submit_seller_verification(
    body: SellerVerificationSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit PAN + Aadhaar for seller KYC. Marks seller as verified after format checks.
    No separate admin step — add a KYC vendor or manual review later if you need it.
    In production: encrypt at rest; consider UIDAI / regulated verification where required.
    """
    if not current_user.is_seller:
        raise HTTPException(status_code=400, detail="Enable seller mode to submit verification")
    sp = current_user.seller_profile
    if sp is not None and sp.verification_status == "verified":
        raise HTTPException(status_code=400, detail="Already verified as seller")

    if sp is None:
        sp = SellerProfile(user_id=current_user.id)
        db.add(sp)
    if body.date_of_birth is not None:
        sp.date_of_birth = body.date_of_birth
    if body.sex is not None:
        sp.sex = body.sex
    if sp.date_of_birth is None or sp.sex is None:
        raise HTTPException(
            status_code=400,
            detail="Date of birth and sex are required for sellers. Register as a seller or include them in this request.",
        )
    sp.pan_number = body.pan_number
    sp.aadhaar_number = body.aadhaar_number
    sp.verification_status = "verified"
    db.commit()
    db.refresh(current_user)
    return current_user
