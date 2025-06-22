from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.transcript import (
    TranscriptRequest, 
    TranscriptResponse, 
    TranscriptListResponse,
    ErrorResponse
)
from app.services.youtube_service import youtube_service
from app.services.storage_services import storage_service

router = APIRouter()

@router.post("/extract", response_model=TranscriptResponse)
async def extract_transcript(request: TranscriptRequest):
    """
    Extract transcript from YouTube video.
    
    This endpoint:
    1. Extracts video ID from URL
    2. Fetches available transcripts
    3. Selects best available transcript (prioritizes English, manual over generated)
    4. Saves transcript to storage
    5. Returns complete transcript data
    """
    try:
        # Extract video ID to check if we already have it
        video_id = youtube_service.extract_video_id(str(request.video_url))
        
        if video_id:
            # Check if we already have this transcript
            existing_transcript = await storage_service.get_transcript(video_id)
            if existing_transcript and existing_transcript.status.value == "completed":
                return existing_transcript
        
        # Extract transcript
        transcript = await youtube_service.get_transcript(str(request.video_url))
        
        # Save if successful
        if transcript.status.value == "completed":
            await storage_service.save_transcript(transcript)
        
        return transcript
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/list", response_model=TranscriptListResponse)
async def list_transcripts(
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of transcripts to return")
):
    """
    List all stored transcripts.
    
    Returns a list of transcript summaries including:
    - Video ID and URL
    - Status and language
    - Transcript count and preview
    - Timestamp
    """
    try:
        transcripts = await storage_service.list_transcripts(limit=limit)
        
        return TranscriptListResponse(
            transcripts=transcripts,
            total=len(transcripts)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/{video_id}", response_model=TranscriptResponse)
async def get_transcript(video_id: str):
    """
    Get stored transcript by video ID.
    
    Returns the complete transcript data if it exists in storage.
    """
    try:
        transcript = await storage_service.get_transcript(video_id)
        
        if not transcript:
            raise HTTPException(
                status_code=404,
                detail=f"Transcript not found for video ID: {video_id}"
            )
        
        return transcript
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.delete("/{video_id}")
async def delete_transcript(video_id: str):
    """
    Delete stored transcript by video ID.
    """
    try:
        success = await storage_service.delete_transcript(video_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Transcript not found for video ID: {video_id}"
            )
        
        return {"message": f"Transcript deleted successfully for video ID: {video_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health/check")
async def health_check():
    """
    Simple health check endpoint.
    """
    return {
        "status": "healthy",
        "service": "YouTube Transcript API",
        "version": "1.0.0"
    }