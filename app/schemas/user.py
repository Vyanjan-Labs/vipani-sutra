from datetime import date, datetime
import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

_PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")

SellerSex = Literal["male", "female", "other", "prefer_not_to_say"]


def _age_from_date_of_birth(date_of_birth: Optional[date]) -> Optional[int]:
    if date_of_birth is None:
        return None
    today = date.today()
    return today.year - date_of_birth.year - (
        (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
    )


class PhoneProfileRegistrationRequest(BaseModel):
    """Registration by phone. City and address are optional for buyers and sellers. Sellers must still provide shop name, date of birth, and sex when is_seller is true."""

    name: str
    phone: str
    city: Optional[str] = None
    address: Optional[str] = None
    shop_name: Optional[str] = None
    is_buyer: bool = True
    is_seller: bool = False
    date_of_birth: Optional[date] = None
    sex: Optional[SellerSex] = None

    @field_validator("city", "address", "shop_name", mode="before")
    @classmethod
    def strip_optional_text_fields(cls, value: object) -> Optional[str]:
        if value is None:
            return None
        stripped = str(value).strip()
        return stripped if stripped else None

    @model_validator(mode="after")
    def roles_and_seller_fields(self):
        if not self.is_buyer and not self.is_seller:
            raise ValueError("Choose at least one of buyer or seller")
        if self.is_seller:
            if not self.shop_name:
                raise ValueError("Sellers must provide shop name")
            if self.date_of_birth is None or self.sex is None:
                raise ValueError("Sellers must provide date of birth and sex")
        return self


class BuyerProfileOut(BaseModel):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SellerProfileOut(BaseModel):
    """Public seller profile — no PAN/Aadhaar in API responses. Age is derived from date_of_birth."""

    id: int
    shop_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    sex: Optional[str] = None
    verification_status: str
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def age(self) -> Optional[int]:
        return _age_from_date_of_birth(self.date_of_birth)

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    city: Optional[str] = None
    address: Optional[str] = None
    firebase_uid: Optional[str] = None
    is_buyer: bool
    is_seller: bool
    buyer_profile: Optional[BuyerProfileOut] = None
    seller_profile: Optional[SellerProfileOut] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AccessTokenWithUserResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class FirebaseSignInRequest(BaseModel):
    id_token: str = Field(..., min_length=10)


class FirebasePhoneRegistrationRequest(PhoneProfileRegistrationRequest):
    """Same profile as phone registration, plus Firebase ID token (verified phone must match `phone`)."""

    id_token: str = Field(..., min_length=10)


class SellerVerificationSubmit(BaseModel):
    pan_number: str = Field(..., min_length=1)
    aadhaar_number: str = Field(..., min_length=1)
    date_of_birth: Optional[date] = None
    sex: Optional[SellerSex] = None

    @field_validator("pan_number", mode="before")
    @classmethod
    def normalize_pan(cls, value: object) -> str:
        normalized = str(value).strip().upper()
        if not _PAN_RE.match(normalized):
            raise ValueError("Invalid PAN format (expected e.g. ABCDE1234F)")
        return normalized

    @field_validator("aadhaar_number", mode="before")
    @classmethod
    def normalize_aadhaar(cls, value: object) -> str:
        digits_only = "".join(c for c in str(value) if c.isdigit())
        if len(digits_only) != 12:
            raise ValueError("Aadhaar must be 12 digits")
        return digits_only
