from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from urllib.parse import urlparse, parse_qs
import re
import logging
from typing import Optional, List, Tuple
from app.models.transcript import TranscriptData, TranscriptSegment, TranscriptStatus

# Setup logging
logger = logging.getLogger(__name__)

class YouTubeService:
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
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
                # Clean video ID (remove any extra parameters)
                video_id = re.sub(r'[^a-zA-Z0-9_-].*', '', video_id)
                return video_id
        return None

    @staticmethod
    def get_transcript(video_url: str, language: Optional[str] = None, timeout: int = 30) -> TranscriptData:
        """
        Get transcript from YouTube video with improved error handling.
        
        Args:
            video_url (str): YouTube video URL
            language (Optional[str], optional): Preferred language code. Defaults to None.
            timeout (int): Request timeout in seconds. Defaults to 30.
            
        Returns:
            TranscriptData: Transcript data with status
        """
        transcript_data = TranscriptData(
            youtube_url=video_url,
            status=TranscriptStatus.PROCESSING
        )
        
        try:
            logger.info(f"Processing transcript for URL: {video_url}")
            
            # Validate and extract video ID
            video_id = YouTubeService.extract_video_id(video_url)
            if not video_id:
                logger.error(f"Invalid YouTube URL: {video_url}")
                transcript_data.status = TranscriptStatus.FAILED
                transcript_data.error_message = "Invalid YouTube URL format"
                return transcript_data
            
            logger.info(f"Extracted video ID: {video_id}")
            
            # Get available transcripts with timeout handling
            try:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                logger.info(f"Retrieved transcript list for video: {video_id}")
            except Exception as e:
                logger.error(f"Failed to list transcripts for {video_id}: {str(e)}")
                transcript_data.status = TranscriptStatus.FAILED
                transcript_data.error_message = f"Cannot access video transcripts: {str(e)}"
                return transcript_data
            
            # Try to get transcript in preferred order
            transcript = None
            selected_language = None
            
            # Priority order for language selection
            if language:
                try:
                    transcript = transcript_list.find_transcript([language])
                    selected_language = language
                    logger.info(f"Found transcript in requested language: {language}")
                except Exception as e:
                    logger.warning(f"Requested language {language} not found: {str(e)}")
                    
            if not transcript:
                # Try auto-generated English
                try:
                    transcript = transcript_list.find_generated_transcript(['en'])
                    selected_language = 'en'
                    logger.info("Using auto-generated English transcript")
                except Exception as e:
                    logger.warning(f"Auto-generated English not found: {str(e)}")
                    
            if not transcript:
                # Try manually created transcripts
                try:
                    manual_transcripts = transcript_list._manually_created_transcripts
                    if manual_transcripts:
                        transcript = list(manual_transcripts.values())[0]
                        selected_language = transcript.language_code
                        logger.info(f"Using manual transcript in language: {selected_language}")
                except Exception as e:
                    logger.warning(f"No manual transcripts found: {str(e)}")
                    
            if not transcript:
                # Try any generated transcript
                try:
                    generated_transcripts = transcript_list._generated_transcripts
                    if generated_transcripts:
                        transcript = list(generated_transcripts.values())[0]
                        selected_language = transcript.language_code
                        logger.info(f"Using generated transcript in language: {selected_language}")
                except Exception as e:
                    logger.warning(f"No generated transcripts found: {str(e)}")
                        
            if not transcript:
                logger.error(f"No transcript available for video: {video_id}")
                transcript_data.status = TranscriptStatus.FAILED
                transcript_data.error_message = "No transcript available for this video"
                return transcript_data
            
            # Fetch transcript data with error handling
            try:
                logger.info(f"Fetching transcript data for video: {video_id}")
                transcript_entries = transcript.fetch()
                
                if not transcript_entries:
                    logger.error(f"Empty transcript data for video: {video_id}")
                    transcript_data.status = TranscriptStatus.FAILED
                    transcript_data.error_message = "Transcript data is empty"
                    return transcript_data
                    
                logger.info(f"Retrieved {len(transcript_entries)} transcript entries")
                
            except Exception as e:
                logger.error(f"Failed to fetch transcript data: {str(e)}")
                transcript_data.status = TranscriptStatus.FAILED
                transcript_data.error_message = f"Failed to fetch transcript: {str(e)}"
                return transcript_data
            
            # Convert to our format
            segments = []
            full_text_parts = []
            
            for i, entry in enumerate(transcript_entries):
                try:
                    # Access attributes directly from FetchedTranscriptSnippet object
                    segment = TranscriptSegment(
                        start=float(entry.start) if hasattr(entry, 'start') else 0.0,
                        duration=float(entry.duration) if hasattr(entry, 'duration') else 0.0,
                        text=entry.text.strip() if hasattr(entry, 'text') and entry.text else ''
                    )
                    segments.append(segment)
                    if segment.text:  # Only add non-empty text
                        full_text_parts.append(segment.text)
                except Exception as e:
                    logger.warning(f"Error processing segment {i}: {str(e)}")
                    continue
                    
            if not segments:
                logger.error("No valid segments found in transcript")
                transcript_data.status = TranscriptStatus.FAILED
                transcript_data.error_message = "No valid transcript segments found"
                return transcript_data
            
            # Build final transcript data
            transcript_data.segments = segments
            transcript_data.full_text = ' '.join(full_text_parts)
            transcript_data.language = selected_language or 'unknown'
            transcript_data.video_id = video_id
            transcript_data.status = TranscriptStatus.COMPLETED
            
            # Try to get video title (optional)
            try:
                transcript_data.video_title = f"Video {video_id}"
                # You can implement actual title fetching here using pytube or YouTube API
            except Exception as e:
                logger.warning(f"Could not fetch video title: {str(e)}")
            
            logger.info(f"Successfully processed transcript for video: {video_id}")
            
        except Exception as e:
            logger.error(f"Unexpected error processing transcript: {str(e)}")
            transcript_data.status = TranscriptStatus.FAILED
            transcript_data.error_message = f"Unexpected error: {str(e)}"
            
        return transcript_data

    @staticmethod
    def validate_youtube_url(url: str) -> bool:
        """Validate if URL is a proper YouTube URL."""
        if not url:
            return False
        return YouTubeService.extract_video_id(url) is not None