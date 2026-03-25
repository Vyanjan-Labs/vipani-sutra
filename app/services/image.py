import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from app.core.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

async def upload_image(file: UploadFile, folder: str = "vipani/listings") -> str:
    contents = await file.read()
    result = cloudinary.uploader.upload(
        contents,
        folder=folder,
        resource_type="image",
        transformation=[{"width": 800, "crop": "limit"}],  # max 800px wide
    )
    return result["secure_url"]

async def delete_image(public_id: str):
    cloudinary.uploader.destroy(public_id)
