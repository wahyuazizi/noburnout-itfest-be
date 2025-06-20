from youtube_transcript_api import YoutubeTranscriptApi
from urlib.parse import urlparse, parse_qs
import re
from typing import Optional, List, Tuple
from app.models.transcript import TranscriptData, TranscriptSegment, TranscriptStatus

class YouTubeService:
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract Yt video ID from URL."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def get_transcript(video_url: str, language: Optional[str] = None) -> TranscriptData:
        """_summary_

        Args:
            video_url (str): _description_
            language (Optional[str], optional): _description_. Defaults to None.

        Returns:
            TranscriptData: _description_
        """
        transcript_data = TranscriptData(
            youtube_url=video_url,
            status=TranscriptStatus.PROCESSING
        )
        
        try:
            video_id = YouTubeService.extract_video_id(video_url)
            if not video_id:
                transcript_data.status = TranscriptStatus.FAILED
                transcript_data.error_message = "Invalid Youtube URL"
                return transcript_data
            
            # Get available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get transcript in specified lang or auto-generate
            transcript = None
            if language:
                try:
                    transcript = transcript_list.find_transcript([language])
                except:
                    pass
                
            if not transcript:
                # Try auto-generate English first, then any available
                try:
                    transcript= transcript_list.find_generated_transcript(['en'])
                except:
                    # Get first available transcript
                    available = transcript_list._manually_created_transcripts
                    if not available:
                        available = transcript_list._generated_transcriptss
                    if available:
                        transcript = list(available.values())[0]
                        
            if not transcript:
                transcript_data.status = TranscriptStatus.FAILED
                transcript_data.error_message = "No transcript available for this video"
                return transcript_data
            
            # Fetch transcript data
            transcript_entries = transcript.fetch()
            
            # Convert to our format
            segments = []
            full_text_parts = []
            
            for entry in transcript_entries:
                segment = TranscriptSegment(
                    start=entry['start'],
                    duration=entry['duration'],
                    text=entry['text']
                )
                segments.append(segment)
                full_text_parts.append(entry['text'])
                
            transcript_data.segments = segments
            transcript_data.full_text = ' '.join(full_text_parts)
            transcript_data.language = transcript.language_code
            transcript_data.status = TranscriptStatus.COMPLETED
            
            # Try to get video title (basic implementation)
            try:
                # This is a simple approach - in production might use pytube or YouTube API
                transcript_data.video_title = f"Video {video_id}"
            except:
                pass
            
        except Exception as e:
            transcript_data.status = TranscriptStatus.FAILED
            transcript_data.error_message = str(e)
            
        return transcript_data