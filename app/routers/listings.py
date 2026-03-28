from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.listing import Listing
from app.models.user import User
from app.schemas.listing import ListingCreate, ListingUpdate, ListingOut
from app.services.image import upload_image

router = APIRouter(prefix="/listings", tags=["listings"])


def _seller_kyc_verified(user: User) -> bool:
    sp = user.seller_profile
    return sp is not None and sp.verification_status == "verified"

CATEGORIES = [
    "Sports", "Clothes", "Electronics", "Grocery",
    "Furniture", "Books", "Stationery", "Other"
]

@router.get("", response_model=List[ListingOut])
def get_listings(
    city: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Browse all active listings with optional filters. No login required."""
    query = db.query(Listing).filter(Listing.status == "active")

    if city:
        query = query.filter(Listing.city.ilike(f"%{city}%"))
    if category:
        query = query.filter(Listing.category == category)
    if search:
        query = query.filter(Listing.title.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(Listing.price >= min_price)
    if max_price is not None:
        query = query.filter(Listing.price <= max_price)

    return query.order_by(Listing.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/categories")
def get_categories():
    return {"categories": CATEGORIES}

@router.get("/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """Get a single listing. No login required."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing

@router.post("", response_model=ListingOut)
def create_listing(
    body: ListingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new listing. Login required; seller must be KYC-verified."""
    if not current_user.is_seller:
        raise HTTPException(status_code=403, detail="Enable seller mode to post listings")
    if not _seller_kyc_verified(current_user):
        raise HTTPException(
            status_code=403,
            detail="Seller verification required. Submit PAN and Aadhaar, then wait for approval.",
        )
    listing = Listing(**body.model_dump(), user_id=current_user.id, images=[])
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing

@router.post("/{listing_id}/images", response_model=ListingOut)
async def upload_listing_images(
    listing_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload images for a listing. Max 5 images."""
    if not _seller_kyc_verified(current_user):
        raise HTTPException(
            status_code=403,
            detail="Seller verification required before managing listings.",
        )
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your listing")
    if len(files) + len(listing.images) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 images per listing")

    urls = [await upload_image(f) for f in files]
    listing.images = listing.images + urls
    db.commit()
    db.refresh(listing)
    return listing

@router.patch("/{listing_id}", response_model=ListingOut)
def update_listing(
    listing_id: int,
    body: ListingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not _seller_kyc_verified(current_user):
        raise HTTPException(
            status_code=403,
            detail="Seller verification required to edit listings.",
        )
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your listing")

    data = body.model_dump(exclude_unset=True)
    if "buyer_user_id" in data and data["buyer_user_id"] is not None:
        bid = data["buyer_user_id"]
        if bid == listing.user_id:
            raise HTTPException(status_code=400, detail="Buyer cannot be the listing owner")
        buyer = db.query(User).filter(User.id == bid).first()
        if not buyer:
            raise HTTPException(status_code=400, detail="Invalid buyer user id")

    for key, value in data.items():
        setattr(listing, key, value)
    db.commit()
    db.refresh(listing)
    return listing

@router.delete("/{listing_id}")
def delete_listing(
    listing_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete(listing)
    db.commit()
    return {"message": "Listing deleted"}
