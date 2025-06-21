from fastapi import APIRouter
from app.api.v1.endpoints import transcript, #download

api_router = APIRouter()

api_router.include_router(
    transcript.router,
    prefix="/transcript",
    tags=["transcript"]
)

api_router.include_router(
    download.router,
    prefix="/download",
    tags=["download"]
)