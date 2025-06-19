"""
transcript.py
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

class TranscriptStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscriptSegment(BaseModel):
    start: float
    duration: float
    text: str

class TranscriptData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    youtube_url: HttpUrl
    video_title: Optional[str] = None
    video_duration: Optional[int] = None
    language: Optional[str] = None
    segments: List[TranscriptSegment] = []
    full_text: Optional[str] = None
    status: TranscriptStatus = TranscriptStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    error_message: Optional[str] = None

class TranscriptRequest(BaseModel):
    youtube_url: HttpUrl
    language: Optional[str] = None

class TranscriptResponse(BaseModel):
    id: str
    status: TranscriptStatus
    youtube_url: str
    video_title: Optional[str] = None
    created_at: datetime
    message: Optional[str] = None