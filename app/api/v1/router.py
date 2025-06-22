# app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.endpoints import transcript, ai

api_router = APIRouter()

# Include transcript endpoints
api_router.include_router(
    transcript.router,
    prefix="/transcript",
    tags=["transcript"]
)

# Include AI endpoints
api_router.include_router(
    ai.router,
    prefix="/ai",
    tags=["ai"]
)