# app/api/v1/endpoints/ai.py
from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.models.ai_models import (
    SummaryRequest,
    SummaryResponse,
    StudyPlanRequest,
    StudyPlanResponse
)
from app.services.azure_service import azure_service
from app.services.storage_services import storage_service

router = APIRouter()

@router.post("/summary", response_model=SummaryResponse)
async def create_summary(request: SummaryRequest):
    """
    Create a summary from YouTube transcript.
    
    This endpoint:
    1. Retrieves the stored transcript by video ID
    2. Uses Azure OpenAI to generate a concise summary
    3. Returns the summary with metadata
    """
    try:
        # Get the transcript
        transcript_response = await storage_service.get_transcript(request.video_id)
        
        if not transcript_response:
            raise HTTPException(
                status_code=404,
                detail=f"Transcript not found for video ID: {request.video_id}"
            )
        
        if transcript_response.status.value != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Transcript is not ready. Status: {transcript_response.status.value}"
            )
        
        # Extract transcript text - check the correct attribute name
        # Common attribute names: entries, segments, content, text, data
        transcript_text = ""
        
        # Try different possible attribute names based on your model structure
        if hasattr(transcript_response, 'entries') and transcript_response.entries:
            transcript_text = " ".join([entry.text for entry in transcript_response.entries])
        elif hasattr(transcript_response, 'segments') and transcript_response.segments:
            transcript_text = " ".join([segment.text for segment in transcript_response.segments])
        elif hasattr(transcript_response, 'content') and transcript_response.content:
            transcript_text = transcript_response.content
        elif hasattr(transcript_response, 'text') and transcript_response.text:
            transcript_text = transcript_response.text
        elif hasattr(transcript_response, 'data') and transcript_response.data:
            # If data is a list of transcript entries
            if isinstance(transcript_response.data, list):
                transcript_text = " ".join([item.text if hasattr(item, 'text') else str(item) for item in transcript_response.data])
            else:
                transcript_text = str(transcript_response.data)
        else:
            # Debug: Print available attributes
            available_attrs = [attr for attr in dir(transcript_response) if not attr.startswith('_')]
            raise HTTPException(
                status_code=500,
                detail=f"Unable to find transcript text. Available attributes: {available_attrs}"
            )
        
        if not transcript_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Transcript is empty or contains no text"
            )
        
        # Generate summary using Azure OpenAI
        summary = await azure_service.create_summary(
            transcript_text=transcript_text,
            max_tokens=request.max_length
        )
        
        # Count words in summary
        word_count = len(summary.split())
        
        return SummaryResponse(
            video_id=request.video_id,
            summary=summary,
            created_at=datetime.now(),
            word_count=word_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/study-plan", response_model=StudyPlanResponse)
async def create_study_plan(request: StudyPlanRequest):
    """
    Create a study plan from YouTube transcript.
    
    This endpoint:
    1. Retrieves the stored transcript by video ID
    2. Uses Azure OpenAI to generate a structured study plan
    3. Returns the study plan with metadata
    """
    try:
        # Get the transcript
        transcript_response = await storage_service.get_transcript(request.video_id)
        
        if not transcript_response:
            raise HTTPException(
                status_code=404,
                detail=f"Transcript not found for video ID: {request.video_id}"
            )
        
        if transcript_response.status.value != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Transcript is not ready. Status: {transcript_response.status.value}"
            )
        
        # Extract transcript text - using the same logic as above
        transcript_text = ""
        
        if hasattr(transcript_response, 'entries') and transcript_response.entries:
            transcript_text = " ".join([entry.text for entry in transcript_response.entries])
        elif hasattr(transcript_response, 'segments') and transcript_response.segments:
            transcript_text = " ".join([segment.text for segment in transcript_response.segments])
        elif hasattr(transcript_response, 'content') and transcript_response.content:
            transcript_text = transcript_response.content
        elif hasattr(transcript_response, 'text') and transcript_response.text:
            transcript_text = transcript_response.text
        elif hasattr(transcript_response, 'data') and transcript_response.data:
            if isinstance(transcript_response.data, list):
                transcript_text = " ".join([item.text if hasattr(item, 'text') else str(item) for item in transcript_response.data])
            else:
                transcript_text = str(transcript_response.data)
        else:
            available_attrs = [attr for attr in dir(transcript_response) if not attr.startswith('_')]
            raise HTTPException(
                status_code=500,
                detail=f"Unable to find transcript text. Available attributes: {available_attrs}"
            )
        
        if not transcript_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Transcript is empty or contains no text"
            )
        
        # Generate study plan using Azure OpenAI
        study_plan = await azure_service.create_study_plan(
            transcript_text=transcript_text,
            study_duration=request.duration
        )
        
        return StudyPlanResponse(
            video_id=request.video_id,
            study_plan=study_plan,
            duration=request.duration,
            created_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health/check")
async def ai_health_check():
    """
    Health check endpoint for AI services.
    """
    try:
        # You can add a simple test call to Azure OpenAI here if needed
        return {
            "status": "healthy",
            "service": "AI Services",
            "azure_endpoint": azure_service.client._base_url if hasattr(azure_service.client, '_base_url') else "configured",
            "deployment": azure_service.deployment_name
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI service unavailable: {str(e)}"
        )

# Debug endpoint to inspect transcript structure
@router.get("/debug/transcript/{video_id}")
async def debug_transcript_structure(video_id: str):
    """
    Debug endpoint to inspect the structure of a transcript response.
    Remove this in production.
    """
    try:
        transcript_response = await storage_service.get_transcript(video_id)
        
        if not transcript_response:
            return {"error": "Transcript not found"}
        
        # Get all non-private attributes
        attributes = {}
        for attr in dir(transcript_response):
            if not attr.startswith('_'):
                try:
                    value = getattr(transcript_response, attr)
                    if not callable(value):
                        attributes[attr] = str(type(value))
                except:
                    attributes[attr] = "Could not access"
        
        return {
            "video_id": video_id,
            "transcript_type": str(type(transcript_response)),
            "available_attributes": attributes,
            "status": transcript_response.status.value if hasattr(transcript_response, 'status') else "No status"
        }
        
    except Exception as e:
        return {"error": str(e)}