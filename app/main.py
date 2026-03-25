from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.routers import auth, listings, users, admin

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Hyperlocal listings platform — list anything, discover locally.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # vipani-darshan dev URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(users.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"app": settings.APP_NAME, "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}
