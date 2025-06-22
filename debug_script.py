#!/usr/bin/env python3
"""
Debug script untuk test YouTube transcript langsung dengan perbaikan
"""

import json
import sys
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import re
from typing import Optional, Dict, Any

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
            video_id = re.sub(r'[^a-zA-Z0-9_-].*', '', video_id)
            return video_id
    return None

def test_youtube_transcript(video_url: str) -> Dict[str, Any]:
    """Test YouTube transcript extraction with detailed logging."""
    
    result = {
        "status": "processing",
        "video_url": video_url,
        "video_id": None,
        "error": None,
        "transcript_count": 0,
        "available_languages": [],
        "selected_language": None,
        "transcript_preview": None,
        "full_transcript": None,
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        print(f"🔍 Testing URL: {video_url}")
        
        # Step 1: Extract video ID
        video_id = extract_video_id(video_url)
        if not video_id:
            result["status"] = "failed"
            result["error"] = "Invalid YouTube URL"
            print("❌ Invalid YouTube URL")
            return result
            
        result["video_id"] = video_id
        print(f"✅ Video ID extracted: {video_id}")
        
        # Step 2: List available transcripts with proper error handling
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            print("✅ Successfully connected to YouTube")
        except TranscriptsDisabled:
            result["status"] = "failed"
            result["error"] = "Transcripts are disabled for this video"
            print("❌ Transcripts disabled for this video")
            return result
        except NoTranscriptFound:
            result["status"] = "failed" 
            result["error"] = "No transcripts found for this video"
            print("❌ No transcripts found")
            return result
        except Exception as e:
            result["status"] = "failed"
            result["error"] = f"Failed to access video: {str(e)}"
            print(f"❌ Error accessing video: {str(e)}")
            return result
        
        # Step 3: Get available languages
        available_languages = []
        manual_transcripts = []
        generated_transcripts = []
        
        try:
            for transcript in transcript_list:
                lang_info = {
                    "language": transcript.language,
                    "language_code": transcript.language_code,
                    "is_generated": transcript.is_generated,
                    "is_translatable": transcript.is_translatable
                }
                available_languages.append(lang_info)
                
                if transcript.is_generated:
                    generated_transcripts.append(transcript)
                else:
                    manual_transcripts.append(transcript)
                    
            result["available_languages"] = available_languages
            print(f"✅ Found {len(available_languages)} available transcripts:")
            for lang in available_languages:
                print(f"   - {lang['language']} ({lang['language_code']}) - {'Generated' if lang['is_generated'] else 'Manual'}")
                
        except Exception as e:
            print(f"⚠️ Error listing languages: {str(e)}")
        
        # Step 4: Try to get a transcript dengan priority yang diperbaiki
        transcript = None
        selected_language = None
        
        # Priority: Manual English variants -> Generated English variants -> Any Manual -> Any Generated
        english_codes = ['en', 'en-US', 'en-GB', 'en-CA', 'en-AU']
        
        # Try manual English variants first
        for transcript_source, source_name in [(manual_transcripts, "manual"), (generated_transcripts, "generated")]:
            if transcript:
                break
                
            # Try English variants
            for lang_code in english_codes:
                for t in transcript_source:
                    if t.language_code == lang_code:
                        transcript = t
                        selected_language = t.language_code
                        print(f"✅ Selected {source_name} {t.language} transcript ({selected_language})")
                        break
                if transcript:
                    break
                    
            # If no English variants, try first available in this category
            if not transcript and transcript_source:
                transcript = transcript_source[0]
                selected_language = transcript.language_code
                print(f"✅ Selected {source_name} transcript in {transcript.language} ({selected_language})")
        
        if not transcript:
            result["status"] = "failed"
            result["error"] = "No usable transcript found"
            print("❌ No usable transcript found")
            return result
            
        result["selected_language"] = selected_language
        
        # Step 5: Fetch transcript data
        try:
            print("📥 Fetching transcript data...")
            transcript_entries = transcript.fetch()
            
            if not transcript_entries:
                result["status"] = "failed"
                result["error"] = "Transcript data is empty"
                print("❌ Transcript data is empty")
                return result
                
            result["transcript_count"] = len(transcript_entries)
            print(f"✅ Retrieved {len(transcript_entries)} transcript segments")
            
            # Process transcript dengan error handling yang lebih baik
            segments = []
            full_text_parts = []
            
            for i, entry in enumerate(transcript_entries):
                try:
                    # Debug: log entry structure for first few entries
                    if i < 3:
                        print(f"   Debug entry {i}: type={type(entry)}, attributes={[attr for attr in dir(entry) if not attr.startswith('_')]}")
                    
                    # Access attributes directly from FetchedTranscriptSnippet object
                    segment = {
                        "start": float(getattr(entry, 'start', 0.0)),
                        "duration": float(getattr(entry, 'duration', 0.0)),
                        "text": getattr(entry, 'text', '').strip()
                    }
                    
                    segments.append(segment)
                    if segment['text']:
                        full_text_parts.append(segment['text'])
                        
                except Exception as e:
                    print(f"⚠️ Error processing segment {i}: {str(e)}")
                    # More detailed debug info
                    print(f"   Entry: {entry}")
                    if hasattr(entry, '__dict__'):
                        print(f"   Entry dict: {entry.__dict__}")
                    continue
            
            if not segments:
                result["status"] = "failed"
                result["error"] = "No valid segments processed"
                print("❌ No valid segments processed")
                return result
            
            # Build final result
            full_text = ' '.join(full_text_parts)
            result["full_transcript"] = full_text
            result["transcript_preview"] = full_text[:200] + "..." if len(full_text) > 200 else full_text
            result["status"] = "completed"
            
            print(f"✅ Successfully processed transcript:")
            print(f"   - Total segments: {len(segments)}")
            print(f"   - Total characters: {len(full_text)}")
            print(f"   - Preview: {result['transcript_preview']}")
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = f"Failed to fetch transcript: {str(e)}"
            print(f"❌ Error fetching transcript: {str(e)}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return result
            
    except Exception as e:
        result["status"] = "failed"
        result["error"] = f"Unexpected error: {str(e)}"
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
    
    return result

def main():
    """Main function to test YouTube transcript."""
    
    # Test URLs - gunakan URL dari error log Anda
    test_urls = [
        "https://www.youtube.com/watch?v=Y681hXWwhQY",  # URL dari error log
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll - has transcript
    ]
    
    # Atau ambil URL dari command line argument
    if len(sys.argv) > 1:
        test_urls = [sys.argv[1]]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print('='*60)
        
        result = test_youtube_transcript(url)
        
        # Save result to JSON file
        filename = f"transcript_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Result saved to: {filename}")
            
            # Check if file is actually written and not empty
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.strip():
                    print(f"✅ File contains {len(content)} characters")
                else:
                    print("❌ File is empty!")
                    
        except Exception as e:
            print(f"❌ Error saving file: {str(e)}")
        
        print(f"\nFinal Status: {result['status'].upper()}")
        if result['error']:
            print(f"Error: {result['error']}")

if __name__ == "__main__":
    main()