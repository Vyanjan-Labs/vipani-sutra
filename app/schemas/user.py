from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp: str

class UserCreate(BaseModel):
    name: str
    phone: str
    city: str
    shop_name: Optional[str] = None

class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    city: str
    role: str
    shop_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
