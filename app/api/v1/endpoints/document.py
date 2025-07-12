# app/api/v1/endpoints/document.py
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse

from app.services.document_service import document_service, UPLOAD_DIR
from app.services.presentation_service import presentation_service, PRESENTATION_DIR
from app.services.azure_service import azure_service
from app.models.document_models import DocumentMetadata, PresentationResponse

router = APIRouter()

@router.post("/upload", response_model=DocumentMetadata)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF, DOCX, TXT) for processing.
    """
    supported_extensions = [".pdf", ".docx", ".txt"]
    # Extract extension from filename
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in supported_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Please upload a PDF, DOCX, or TXT file."
        )
        
    try:
        document_id, _ = await document_service.save_uploaded_file(file)
        metadata = DocumentMetadata(
            document_id=document_id,
            file_name=file.filename
        )
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.post("/{document_id}/generate-presentation", response_model=PresentationResponse)
async def generate_presentation(document_id: str):
    """
    Generate a presentation from an uploaded document.
    
    This endpoint:
    1. Finds the uploaded document by its ID.
    2. Extracts text from the document.
    3. Generates a summary using an AI service.
    4. Creates a .pptx presentation from the summary.
    5. Returns a download link for the presentation.
    """
    try:
        # Find the file in the upload directory
        uploaded_files = list(UPLOAD_DIR.glob(f"{document_id}.*"))
        if not uploaded_files:
            raise HTTPException(status_code=404, detail="Document not found.")
        
        file_path = uploaded_files[0]
        
        # 1. Extract text
        text = document_service.extract_text_from_file(file_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="Extracted text is empty.")
            
        # 2. Generate summary
        summary = await azure_service.create_summary(transcript_text=text)
        if not summary.strip():
            raise HTTPException(status_code=500, detail="Failed to generate summary.")

        # 3. Create presentation
        presentation_path = presentation_service.create_presentation_from_summary(document_id, summary)
        
        # 4. Create response with download URL
        response = PresentationResponse(
            document_id=document_id,
            file_name=presentation_path.name,
            download_url=f"/api/v1/document/download/presentation/{document_id}"
        )
        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

@router.get("/download/presentation/{document_id}", response_class=FileResponse)
async def download_presentation(document_id: str):
    """
    Download a generated presentation file.
    """
    try:
        presentation_path = PRESENTATION_DIR / f"{document_id}.pptx"
        if not presentation_path.exists():
            raise HTTPException(status_code=404, detail="Presentation file not found.")
        
        return FileResponse(
            path=presentation_path,
            filename=f"presentation_{document_id}.pptx",
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))