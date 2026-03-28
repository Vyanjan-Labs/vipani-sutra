from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

http_bearer_security = HTTPBearer()


def create_jwt_access_token_for_user(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token_payload(access_token: str) -> dict:
    return jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer_security),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
    )
    try:
        payload = decode_access_token_payload(credentials.credentials)
    except JWTError:
        raise unauthorized from None

    subject_user_id = payload.get("sub")
    if subject_user_id is None:
        raise unauthorized

    user = db.query(User).filter(User.id == int(subject_user_id)).first()
    if user is None:
        raise unauthorized
    return user
