# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.endpoints import document

api_router = APIRouter()

# Include document processing endpoints
api_router.include_router(
    document.router,
    prefix="/document",
    tags=["document"]
)
