from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.auth import create_access_token
from app.models.user import User
from app.schemas.user import OTPRequest, OTPVerify, UserCreate, UserOut, TokenOut
from app.services.otp import send_otp, verify_otp

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/send-otp")
async def send_otp_route(body: OTPRequest):
    """Send OTP to phone number."""
    await send_otp(body.phone)
    return {"message": "OTP sent successfully"}

@router.post("/verify-otp", response_model=TokenOut)
async def verify_otp_route(body: OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP. If user doesn't exist, return needs_registration=True."""
    if not verify_otp(body.phone, body.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = db.query(User).filter(User.phone == body.phone).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found. Please register first.",
            headers={"X-Needs-Registration": "true"}
        )

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "user": user}

@router.post("/register", response_model=TokenOut)
async def register(body: UserCreate, db: Session = Depends(get_db)):
    """Register a new user after OTP is already verified."""
    existing = db.query(User).filter(User.phone == body.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone already registered")

    user = User(**body.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "user": user}
