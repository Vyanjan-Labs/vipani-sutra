from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.listing import Listing
from app.models.rating import Rating
from app.models.user import User
from app.schemas.rating import RatingCreate, RatingOut, RatingUpdate

router = APIRouter(prefix="/listings", tags=["ratings"])


@router.post("/{listing_id}/ratings", response_model=RatingOut)
def create_rating(
    listing_id: int,
    body: RatingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit a rating on a sold listing (from you → to the other party).

    - reputation_scope=seller: you are the buyer; to_user_id becomes the listing owner.
    - reputation_scope=buyer: you are the seller; to_user_id becomes the recorded buyer.
    """
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.status != "sold":
        raise HTTPException(status_code=400, detail="Ratings are only allowed on sold listings")
    if listing.buyer_user_id is None:
        raise HTTPException(
            status_code=400,
            detail="Set buyer_user_id on the listing (mark who bought) before ratings",
        )

    if body.reputation_scope == "seller":
        if current_user.id != listing.buyer_user_id:
            raise HTTPException(status_code=403, detail="Only the buyer can rate the seller here")
        to_uid = listing.user_id
    elif body.reputation_scope == "buyer":
        if current_user.id != listing.user_id:
            raise HTTPException(status_code=403, detail="Only the seller can rate the buyer here")
        to_uid = listing.buyer_user_id
    else:
        raise HTTPException(status_code=400, detail="Invalid reputation_scope")

    if to_uid == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot rate yourself")

    existing = (
        db.query(Rating)
        .filter(
            Rating.listing_id == listing_id,
            Rating.from_user_id == current_user.id,
            Rating.reputation_scope == body.reputation_scope,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="You already submitted this rating for this listing")

    c = (body.comment or "").strip()
    row = Rating(
        listing_id=listing_id,
        from_user_id=current_user.id,
        to_user_id=to_uid,
        reputation_scope=body.reputation_scope,
        stars=body.stars,
        comment=c if c else None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.patch("/{listing_id}/ratings", response_model=RatingOut)
def update_rating(
    listing_id: int,
    body: RatingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Edit your own rating (wrong stars / comment). Only the user who created the rating (from_user_id)
    can update; at least one of stars or comment must be sent.
    """
    payload = body.model_dump(exclude_unset=True)
    if "stars" not in payload and "comment" not in payload:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one of: stars, comment",
        )

    row = (
        db.query(Rating)
        .filter(
            Rating.listing_id == listing_id,
            Rating.from_user_id == current_user.id,
            Rating.reputation_scope == body.reputation_scope,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Rating not found")

    if "stars" in payload:
        row.stars = payload["stars"]
    if "comment" in payload:
        c = payload["comment"]
        if c is None:
            row.comment = None
        else:
            s = str(c).strip()
            row.comment = s if s else None

    db.commit()
    db.refresh(row)
    return row


@router.get("/{listing_id}/ratings", response_model=List[RatingOut])
def list_ratings_for_listing(listing_id: int, db: Session = Depends(get_db)):
    """Public list of ratings left on this listing (both scopes)."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return (
        db.query(Rating)
        .filter(Rating.listing_id == listing_id)
        .order_by(Rating.created_at.desc())
        .all()
    )
