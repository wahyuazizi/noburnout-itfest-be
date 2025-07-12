# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.endpoints import document, auth

api_router = APIRouter()

# Include authentication endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# Include document processing endpoints
api_router.include_router(
    document.router,
    prefix="/document",
    tags=["document"]
)
