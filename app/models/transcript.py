from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TranscriptStatus(str, Enum):
    """Status of transcript processing."""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class LanguageInfo(BaseModel):
    """Information about available transcript language."""
    language: str
    language_code: str
    is_generated: bool
    is_translatable: bool

class TranscriptSegment(BaseModel):
    """Individual transcript segment."""
    start: float = Field(..., description="Start time in seconds")
    duration: float = Field(..., description="Duration in seconds")
    text: str = Field(..., description="Transcript text")

class TranscriptRequest(BaseModel):
    """Request model for YouTube transcript extraction."""
    video_url: HttpUrl = Field(..., description="YouTube video URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            }
        }

class TranscriptResponse(BaseModel):
    """Response model for transcript extraction."""
    status: TranscriptStatus
    video_url: str
    video_id: Optional[str] = None
    error: Optional[str] = None
    transcript_count: int = 0
    available_languages: List[LanguageInfo] = []
    selected_language: Optional[str] = None
    transcript_preview: Optional[str] = None
    full_transcript: Optional[str] = None
    segments: Optional[List[TranscriptSegment]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    processing_time: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TranscriptListResponse(BaseModel):
    """Response model for listing stored transcripts."""
    transcripts: List[Dict[str, Any]]
    total: int
    
class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    status_code: int = 400