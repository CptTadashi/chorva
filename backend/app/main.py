from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.api_router import api_router
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP uchun hamma joydan ruxsat, keyinchalik xavfsizroq qilinadi
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Media fayllarni ochiq qilish
if not os.path.exists("media"):
    os.makedirs("media")

app.mount("/media", StaticFiles(directory="media"), name="media")

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to Chorva va Yem MVP"}
