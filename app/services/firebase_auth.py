"""Firebase Admin: verify ID tokens from the client (Phone / Email sign-in)."""

from __future__ import annotations

import json

import firebase_admin
from firebase_admin import auth, credentials

from app.core.config import settings


def is_firebase_configured() -> bool:
    return bool(settings.FIREBASE_CREDENTIALS_PATH or settings.FIREBASE_CREDENTIALS_JSON)


def _ensure_app() -> None:
    if firebase_admin._apps:
        return
    if settings.FIREBASE_CREDENTIALS_PATH:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
    elif settings.FIREBASE_CREDENTIALS_JSON:
        cred = credentials.Certificate(json.loads(settings.FIREBASE_CREDENTIALS_JSON))
    else:
        raise RuntimeError("Firebase credentials not configured")
    firebase_admin.initialize_app(cred)


def verify_id_token(id_token: str) -> dict:
    """Verify a Firebase ID token; returns decoded claims (uid, phone_number, email, etc.)."""
    _ensure_app()
    return auth.verify_id_token(id_token)


def normalize_phone_digits(phone: str) -> str:
    """Compare Indian mobiles consistently (+91… vs 10 digits)."""
    d = "".join(c for c in phone if c.isdigit())
    if len(d) >= 10:
        return d[-10:]
    return d
