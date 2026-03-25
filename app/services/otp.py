import random
import httpx
from app.core.config import settings

# In-memory OTP store for dev. Replace with Redis in production.
otp_store: dict = {}

def generate_otp(phone: str) -> str:
    otp = str(random.randint(100000, 999999))
    otp_store[phone] = otp
    return otp

def verify_otp(phone: str, otp: str) -> bool:
    stored = otp_store.get(phone)
    if stored and stored == otp:
        del otp_store[phone]
        return True
    return False

async def send_otp_msg91(phone: str, otp: str):
    """Send OTP via MSG91 — works for Indian numbers."""
    url = "https://api.msg91.com/api/v5/otp"
    params = {
        "template_id": settings.MSG91_TEMPLATE_ID,
        "mobile": f"91{phone}",
        "authkey": settings.MSG91_AUTH_KEY,
        "otp": otp,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, params=params)
        return response.json()

async def send_otp(phone: str) -> str:
    otp = generate_otp(phone)
    if settings.ENVIRONMENT == "development":
        # In dev, just print the OTP — no SMS needed
        print(f"[DEV] OTP for {phone}: {otp}")
    else:
        await send_otp_msg91(phone, otp)
    return otp
