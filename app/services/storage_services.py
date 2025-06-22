import json
import aiofiles
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.config import settings
from app.models.transcript import TranscriptResponse

class StorageService:
    """Service for storing and retrieving transcripts."""
    
    def __init__(self):
        self.transcripts_dir = settings.transcripts_dir
        # In-memory cache for quick access
        self._cache: Dict[str, TranscriptResponse] = {}
    
    def _get_file_path(self, video_id: str) -> Path:
        """Get file path for video transcript."""
        return self.transcripts_dir / f"{video_id}.json"
    
    async def save_transcript(self, transcript: TranscriptResponse) -> bool:
        """Save transcript to file and cache."""
        if not transcript.video_id:
            return False
            
        try:
            file_path = self._get_file_path(transcript.video_id)
            
            # Convert to dict for JSON serialization
            data = transcript.model_dump()
            data['timestamp'] = transcript.timestamp.isoformat()
            
            # Save to file
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Save to cache
            self._cache[transcript.video_id] = transcript
            
            return True
            
        except Exception as e:
            print(f"Error saving transcript: {str(e)}")
            return False
    
    async def get_transcript(self, video_id: str) -> Optional[TranscriptResponse]:
        """Get transcript from cache or file."""
        
        # Try cache first
        if video_id in self._cache:
            return self._cache[video_id]
        
        # Try file
        try:
            file_path = self._get_file_path(video_id)
            if not file_path.exists():
                return None
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
                
                # Parse timestamp
                if 'timestamp' in data and isinstance(data['timestamp'], str):
                    data['timestamp'] = datetime.fromisoformat(data['timestamp'])
                
                transcript = TranscriptResponse(**data)
                
                # Add to cache
                self._cache[video_id] = transcript
                
                return transcript
                
        except Exception as e:
            print(f"Error loading transcript: {str(e)}")
            return None
    
    async def list_transcripts(self, limit: int = 100) -> List[Dict[str, Any]]:
        """List all stored transcripts."""
        transcripts = []
        
        try:
            # Get all JSON files in transcripts directory
            for file_path in self.transcripts_dir.glob("*.json"):
                try:
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                        data = json.loads(content)
                        
                        # Add basic info for listing
                        transcript_info = {
                            "video_id": data.get("video_id"),
                            "video_url": data.get("video_url"),
                            "status": data.get("status"),
                            "selected_language": data.get("selected_language"),
                            "transcript_count": data.get("transcript_count", 0),
                            "timestamp": data.get("timestamp"),
                            "transcript_preview": data.get("transcript_preview")
                        }
                        
                        transcripts.append(transcript_info)
                        
                        if len(transcripts) >= limit:
                            break
                            
                except Exception:
                    # Skip invalid files
                    continue
            
            # Sort by timestamp (newest first)
            transcripts.sort(
                key=lambda x: x.get("timestamp", ""), 
                reverse=True
            )
            
        except Exception as e:
            print(f"Error listing transcripts: {str(e)}")
        
        return transcripts
    
    async def delete_transcript(self, video_id: str) -> bool:
        """Delete transcript from file and cache."""
        try:
            # Remove from cache
            if video_id in self._cache:
                del self._cache[video_id]
            
            # Remove file
            file_path = self._get_file_path(video_id)
            if file_path.exists():
                file_path.unlink()
            
            return True
            
        except Exception as e:
            print(f"Error deleting transcript: {str(e)}")
            return False

# Create service instance
storage_service = StorageService()