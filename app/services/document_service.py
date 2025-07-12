# app/services/document_service.py
import os
import uuid
from pathlib import Path
from fastapi import UploadFile
import pypdf
import docx

# Define storage paths
UPLOAD_DIR = Path("app/storage/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class DocumentService:
    """Service for handling document uploads and text extraction."""

    async def save_uploaded_file(self, file: UploadFile) -> (str, Path):
        """
        Saves an uploaded file and returns its ID and path.
        
        Args:
            file: The uploaded file from FastAPI.
            
        Returns:
            A tuple containing the unique document ID and the file path.
        """
        # Generate a unique ID for the document
        document_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        file_path = UPLOAD_DIR / f"{document_id}{file_extension}"
        
        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
            
        return document_id, file_path

    def extract_text_from_file(self, file_path: Path) -> str:
        """
        Extracts text content from a file (PDF, DOCX, TXT).
        
        Args:
            file_path: The path to the file.
            
        Returns:
            The extracted text as a single string.
            
        Raises:
            ValueError: If the file format is unsupported.
        """
        extension = file_path.suffix.lower()
        text = ""
        
        if extension == ".pdf":
            try:
                with open(file_path, "rb") as f:
                    reader = pypdf.PdfReader(f)
                    for page in reader.pages:
                        text += page.extract_text() or ""
            except Exception as e:
                raise ValueError(f"Failed to process PDF file: {e}")
                
        elif extension == ".docx":
            try:
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            except Exception as e:
                raise ValueError(f"Failed to process DOCX file: {e}")

        elif extension == ".txt":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                raise ValueError(f"Failed to read TXT file: {e}")
                
        else:
            raise ValueError(f"Unsupported file format: {extension}")
            
        return text

# Create a singleton instance
document_service = DocumentService()
