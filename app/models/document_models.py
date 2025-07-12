# app/models/document_models.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    """Status of document processing."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class DocumentMetadata(BaseModel):
    """Model for document processing status and metadata."""
    document_id: str = Field(..., description="Unique identifier for the document")
    file_name: str = Field(..., description="Original name of the uploaded file")
    status: ProcessingStatus = Field(default=ProcessingStatus.PENDING, description="Current processing status")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp of upload")
    error_message: Optional[str] = Field(None, description="Details of processing failure, if any")

class PresentationResponse(BaseModel):
    """Response model for a generated presentation."""
    document_id: str = Field(..., description="Identifier of the source document")
    file_name: str = Field(..., description="File name of the generated presentation (e.g., 'summary.pptx')")
    download_url: str = Field(..., description="URL to download the presentation file")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp of presentation creation")
