import re
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

from app.models.transcript import (
    TranscriptResponse, 
    TranscriptStatus, 
    LanguageInfo, 
    TranscriptSegment
)

class YouTubeService:
    """Service for YouTube transcript extraction."""
    
    def __init__(self):
        self.english_codes = ['en', 'en-US', 'en-GB', 'en-CA', 'en-AU']
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL."""
        if not url:
            return None
            
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
            r'youtube\.com\/shorts\/([^&\n?#]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                video_id = re.sub(r'[^a-zA-Z0-9_-].*', '', video_id)
                return video_id
        return None

    async def get_transcript(self, video_url: str) -> TranscriptResponse:
        """
        Extract transcript from YouTube video.
        Based on your working debug script.
        """
        start_time = time.time()
        
        result = TranscriptResponse(
            status=TranscriptStatus.PROCESSING,
            video_url=str(video_url),
            timestamp=datetime.now()
        )
        
        try:
            # Step 1: Extract video ID
            video_id = self.extract_video_id(str(video_url))
            if not video_id:
                result.status = TranscriptStatus.FAILED
                result.error = "Invalid YouTube URL"
                return result
                
            result.video_id = video_id
            
            # Step 2: List available transcripts with proper error handling
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            except TranscriptsDisabled:
                result.status = TranscriptStatus.FAILED
                result.error = "Transcripts are disabled for this video"
                return result
            except NoTranscriptFound:
                result.status = TranscriptStatus.FAILED
                result.error = "No transcripts found for this video"
                return result
            except Exception as e:
                result.status = TranscriptStatus.FAILED
                result.error = f"Failed to access video: {str(e)}"
                return result
            
            # Step 3: Get available languages
            available_languages = []
            manual_transcripts = []
            generated_transcripts = []
            
            try:
                for transcript in transcript_list:
                    lang_info = LanguageInfo(
                        language=transcript.language,
                        language_code=transcript.language_code,
                        is_generated=transcript.is_generated,
                        is_translatable=transcript.is_translatable
                    )
                    available_languages.append(lang_info)
                    
                    if transcript.is_generated:
                        generated_transcripts.append(transcript)
                    else:
                        manual_transcripts.append(transcript)
                        
                result.available_languages = available_languages
                    
            except Exception as e:
                # Continue even if language listing fails
                pass
            
            # Step 4: Try to get a transcript with priority
            transcript = None
            selected_language = None
            
            # Priority: Manual English variants -> Generated English variants -> Any Manual -> Any Generated
            for transcript_source in [manual_transcripts, generated_transcripts]:
                if transcript:
                    break
                    
                # Try English variants first
                for lang_code in self.english_codes:
                    for t in transcript_source:
                        if t.language_code == lang_code:
                            transcript = t
                            selected_language = t.language_code
                            break
                    if transcript:
                        break
                        
                # If no English variants, try first available in this category
                if not transcript and transcript_source:
                    transcript = transcript_source[0]
                    selected_language = transcript.language_code
            
            if not transcript:
                result.status = TranscriptStatus.FAILED
                result.error = "No usable transcript found"
                return result
                
            result.selected_language = selected_language
            
            # Step 5: Fetch transcript data
            try:
                transcript_entries = transcript.fetch()
                
                if not transcript_entries:
                    result.status = TranscriptStatus.FAILED
                    result.error = "Transcript data is empty"
                    return result
                    
                result.transcript_count = len(transcript_entries)
                
                # Process transcript segments
                segments = []
                full_text_parts = []
                
                for entry in transcript_entries:
                    try:
                        segment = TranscriptSegment(
                            start=float(getattr(entry, 'start', 0.0)),
                            duration=float(getattr(entry, 'duration', 0.0)),
                            text=getattr(entry, 'text', '').strip()
                        )
                        
                        segments.append(segment)
                        if segment.text:
                            full_text_parts.append(segment.text)
                            
                    except Exception:
                        # Skip invalid segments
                        continue
                
                if not segments:
                    result.status = TranscriptStatus.FAILED
                    result.error = "No valid segments processed"
                    return result
                
                # Build final result
                full_text = ' '.join(full_text_parts)
                result.full_transcript = full_text
                result.transcript_preview = (
                    full_text[:200] + "..." if len(full_text) > 200 else full_text
                )
                result.segments = segments
                result.status = TranscriptStatus.COMPLETED
                
            except Exception as e:
                result.status = TranscriptStatus.FAILED
                result.error = f"Failed to fetch transcript: {str(e)}"
                return result
                
        except Exception as e:
            result.status = TranscriptStatus.FAILED
            result.error = f"Unexpected error: {str(e)}"
        
        # Add processing time
        result.processing_time = time.time() - start_time
        return result

# Create service instance
youtube_service = YouTubeService()