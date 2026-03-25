from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Vipani"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    MSG91_AUTH_KEY: str = ""
    MSG91_TEMPLATE_ID: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
