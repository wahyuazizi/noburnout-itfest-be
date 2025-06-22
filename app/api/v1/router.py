from fastapi import APIRouter

from app.api.v1.endpoints import transcript

api_router = APIRouter()

# Include transcript endpoints
api_router.include_router(
    transcript.router,
    prefix="/transcript",
    tags=["transcript"]
)