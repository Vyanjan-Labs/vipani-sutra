from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.auth import create_jwt_access_token_for_user
from app.core.database import get_db
from app.models.buyer_profile import BuyerProfile
from app.models.seller_profile import SellerProfile
from app.models.user import User
from app.schemas.user import (
    AccessTokenWithUserResponse,
    FirebasePhoneRegistrationRequest,
    FirebaseSignInRequest,
    PhoneProfileRegistrationRequest,
)
from app.services import firebase_auth

router = APIRouter(prefix="/auth", tags=["auth"])


def _raise_firebase_not_configured_http_exception() -> None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Firebase auth is not configured (set FIREBASE_CREDENTIALS_PATH or FIREBASE_CREDENTIALS_JSON)",
    )


def _verify_client_firebase_id_token_claims(id_token: str) -> dict:
    if not firebase_auth.is_firebase_configured():
        _raise_firebase_not_configured_http_exception()
    try:
        return firebase_auth.verify_id_token(id_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Firebase ID token",
        ) from None


def _require_firebase_uid_from_claims(decoded_claims: dict) -> str:
    firebase_uid = decoded_claims.get("uid")
    if not firebase_uid:
        raise HTTPException(status_code=401, detail="Invalid token claims")
    return firebase_uid


def _require_firebase_phone_number_claim(decoded_claims: dict) -> str:
    phone_number = decoded_claims.get("phone_number")
    if not phone_number:
        raise HTTPException(
            status_code=400,
            detail="Firebase token must include phone_number (use Phone Authentication on the client)",
        )
    return phone_number


def _find_user_by_firebase_uid(db: Session, firebase_uid: str) -> Optional[User]:
    return db.query(User).filter(User.firebase_uid == firebase_uid).first()


def _find_user_by_phone_formats_matching_firebase_token(
    db: Session,
    *,
    normalized_last_10_digits: str,
    raw_phone_from_firebase: str,
) -> Optional[User]:
    if not normalized_last_10_digits:
        return None
    return (
        db.query(User)
        .filter(
            or_(
                User.phone == normalized_last_10_digits,
                User.phone == raw_phone_from_firebase,
                User.phone.like(f"%{normalized_last_10_digits}"),
            )
        )
        .first()
    )


def _persist_firebase_uid_on_user_if_column_empty(
    db: Session,
    user: User,
    firebase_uid: str,
) -> None:
    if user.firebase_uid is not None:
        return
    conflicting_row = (
        db.query(User).filter(User.firebase_uid == firebase_uid, User.id != user.id).first()
    )
    if conflicting_row:
        raise HTTPException(
            status_code=409,
            detail="This Firebase account is linked to another user",
        )
    user.firebase_uid = firebase_uid
    db.commit()
    db.refresh(user)


def _assert_profile_phone_matches_firebase_verified_phone(
    firebase_verified_phone: str,
    submitted_phone: str,
) -> None:
    digits_from_token = firebase_auth.normalize_phone_digits(firebase_verified_phone)
    digits_from_body = firebase_auth.normalize_phone_digits(submitted_phone)
    if digits_from_token != digits_from_body:
        raise HTTPException(
            status_code=400,
            detail="Phone number in profile must match the phone verified by Firebase",
        )


def _ensure_firebase_uid_and_phone_not_already_registered(
    db: Session,
    *,
    firebase_uid: str,
    submitted_phone: str,
) -> None:
    if _find_user_by_firebase_uid(db, firebase_uid):
        raise HTTPException(status_code=400, detail="This Firebase account is already registered")
    if db.query(User).filter(User.phone == submitted_phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")


def _persist_new_user_with_buyer_seller_profiles(
    db: Session,
    profile: PhoneProfileRegistrationRequest,
    *,
    firebase_uid: Optional[str] = None,
) -> User:
    user = User(
        name=profile.name,
        phone=profile.phone,
        city=profile.city,
        address=profile.address,
        is_buyer=profile.is_buyer,
        is_seller=profile.is_seller,
        firebase_uid=firebase_uid,
    )
    db.add(user)
    db.flush()
    if profile.is_buyer:
        db.add(BuyerProfile(user_id=user.id))
    if profile.is_seller:
        db.add(
            SellerProfile(
                user_id=user.id,
                shop_name=profile.shop_name,
                date_of_birth=profile.date_of_birth,
                sex=profile.sex,
            )
        )
    db.commit()
    db.refresh(user)
    return user


@router.post("/register", response_model=AccessTokenWithUserResponse)
async def register_with_phone_profile_only(
    registration_request: PhoneProfileRegistrationRequest,
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.phone == registration_request.phone).first():
        raise HTTPException(status_code=400, detail="Phone already registered")

    user = _persist_new_user_with_buyer_seller_profiles(db, registration_request, firebase_uid=None)
    access_token = create_jwt_access_token_for_user(user.id)
    return {"access_token": access_token, "user": user}


@router.post("/firebase/login", response_model=AccessTokenWithUserResponse)
async def exchange_firebase_id_token_for_session(
    sign_in_request: FirebaseSignInRequest,
    db: Session = Depends(get_db),
):
    decoded_claims = _verify_client_firebase_id_token_claims(sign_in_request.id_token)
    firebase_uid = _require_firebase_uid_from_claims(decoded_claims)

    raw_phone_from_firebase = decoded_claims.get("phone_number") or ""
    normalized_last_10_digits = (
        firebase_auth.normalize_phone_digits(raw_phone_from_firebase) if raw_phone_from_firebase else ""
    )

    user = _find_user_by_firebase_uid(db, firebase_uid)
    if user is None:
        user = _find_user_by_phone_formats_matching_firebase_token(
            db,
            normalized_last_10_digits=normalized_last_10_digits,
            raw_phone_from_firebase=raw_phone_from_firebase,
        )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="No account for this Firebase user. Register with POST /auth/firebase/register first.",
        )

    _persist_firebase_uid_on_user_if_column_empty(db, user, firebase_uid)

    access_token = create_jwt_access_token_for_user(user.id)
    return {"access_token": access_token, "user": user}


@router.post("/firebase/register", response_model=AccessTokenWithUserResponse)
async def register_after_firebase_phone_verification(
    registration_request: FirebasePhoneRegistrationRequest,
    db: Session = Depends(get_db),
):
    decoded_claims = _verify_client_firebase_id_token_claims(registration_request.id_token)
    firebase_uid = _require_firebase_uid_from_claims(decoded_claims)
    firebase_verified_phone = _require_firebase_phone_number_claim(decoded_claims)

    _assert_profile_phone_matches_firebase_verified_phone(
        firebase_verified_phone,
        registration_request.phone,
    )
    _ensure_firebase_uid_and_phone_not_already_registered(
        db,
        firebase_uid=firebase_uid,
        submitted_phone=registration_request.phone,
    )

    profile_only = PhoneProfileRegistrationRequest.model_validate(
        registration_request.model_dump(exclude={"id_token"})
    )
    user = _persist_new_user_with_buyer_seller_profiles(
        db,
        profile_only,
        firebase_uid=firebase_uid,
    )
    access_token = create_jwt_access_token_for_user(user.id)
    return {"access_token": access_token, "user": user}
