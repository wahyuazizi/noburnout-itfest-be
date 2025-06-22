from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SummaryRequest(BaseModel):
    """Request model for creating summary."""
    video_id: str = Field(..., description="YouTube video ID to summarize")
    max_length: Optional[int] = Field(default=500, ge=100, le=1000, description="Maximum tokens for summary")

class SummaryResponse(BaseModel):
    """Response model for summary."""
    video_id: str
    summary: str
    created_at: datetime
    word_count: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class StudyPlanRequest(BaseModel):
    """Request model for creating study plan."""
    video_id: str = Field(..., description="YouTube video ID to create study plan from")
    duration: Optional[str] = Field(default="1 week", description="Study plan duration (e.g., '1 week', '2 weeks', '1 month')")

class StudyPlanResponse(BaseModel):
    """Response model for study plan."""
    video_id: str
    study_plan: str
    duration: str
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }