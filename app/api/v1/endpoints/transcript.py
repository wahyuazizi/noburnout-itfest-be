from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from app.models.transcript import TranscriptRequest, TranscriptResponse, TranscriptData
from app.services.youtube_service import YouTubeService
from app.services.storage_services import storage
# from app.services.ai_service import AIService


router = APIRouter()

@router.post("/", response_model=TranscriptResponse)
async def create_transcript(
    request: TranscriptRequest,
    background_tasks: BackgroundTasks
):
    """Upload YT URL dan ekstrak transkripnya

    Args:
        request (TranscriptRequest): _description_
        background_tasks (BackgroundTasks): _description_
    """
    
    # Start background task to process transcript
    background_tasks.add_task(
        extract_transcript_task,
        str(request.youtube_url),
        request.language
    )
    
    # Return immediate response with initial status
    transcript_data = TranscriptData(
        youtube_url=request.youtube_url,
        status="pending",
    )
    
    # Save to storage
    storage.save_transcript(transcript_data)
    
    return TranscriptResponse(
        id=transcript_data.id,
        status=transcript_data.status,
        youtube_url=str(transcript_data.youtube_url),
        created_at=transcript_data.created_at,
        message="Transkrip sedang diproses. Silakan tunggu beberapa saat.",
    )
    
async def extract_transcript_task(youtube_url: str, language: str = None):
    """Task untuk ekstrak transkrip dari YT URL

    Args:
        youtube_url (str): 
        language (str, optional):  Defaults to None.
    """
    transcript_data = YouTubeService.get_transcript(youtube_url, language)
    storage.save_transcript(transcript_data)

@router.get("/{transcript_id}", response_model=TranscriptData)
async def get_transcript(transcript_id: str):
    """Get transcript by ID
    Args:
        transcript_id (str): 
    """
    
    transcript = storage.get_transcript(transcript_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript

@router.delete("/{transcript_id}/status")
async def get_transcript_status(transcript_id: str):
    """Check transcript processing status"""
    transcript = storage.get_transcript(transcript_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    return {
        "id": transcript.id,
        "status": transcript.status,
        "message": transcript.error_message if transcript.status == "failed" else None
    }
    
@router.post("/{transcript_id}/summary")
async def create_summary(transcript_id: str, background_tasks: BackgroundTasks):
    """Create summary for transcript

    Args:
        transcript_id (str): 
        background_tasks (BackgroundTasks): 
    """
    
    transcript = storage.get_transcript(transcript_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    if transcript.status != "completed":
        raise HTTPException(status_code=400, detail="Transcript is not completed yet")
    
    # Start background task to process summary
    background_tasks.add_task(
        summarize_transcript_task, transcript_id
    )
    return {
        "message": "Ringkasan sedang dibuat. Silakan tunggu beberapa saat.",
        "transcript_id": transcript_id
    }
    
@router.post("/{transcript_id}/study-plan")
async def create_study_plan(transcript_id: str, background_tasks: BackgroundTasks):
    """Create study plan for transcript

    Args:
        transcript_id (str): 
        background_tasks (BackgroundTasks): 
    """
    
    transcript = storage.get_transcript(transcript_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    if transcript.status != "completed":
        raise HTTPException(status_code=400, detail="Transcript is not completed yet")
    
    # Start background task to process study plan
    background_tasks.add_task(
        generate_study_plan_task, transcript_id
    )
    
    return {
        "message": "Rencana belajar sedang dibuat. Silakan tunggu beberapa saat.",
        "transcript_id": transcript_id
    }
    
@router.get("/{transcript_id}")
async def delete_transcript(transcript_id: str):
    """Delete transcript by ID

    Args:
        transcript_id (str): 
    """
    
    success = storage.delete_transcript(transcript_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return {
        "message": "Transkrip berhasil dihapus."
    }
    
@router.get("/")
async def list_transcripts():
    """List all transcripts"""
    
    transcripts = storage.list_transcripts()
    return [
        TranscriptResponse(
            id=t.id,
            status=t.status,
            youtube_url=str(t.youtube_url),
            created_at=t.created_at,
            video_title=t.video_title,
        )
        for t in transcripts
    ]
    
# Background task functions
async def summarize_transcript_task(transcript_id: str):
    """Task to summarize transcript"""
    pass

async def generate_study_plan_task(transcript_id: str):
    """Task to generate study plan from transcript"""
    pass