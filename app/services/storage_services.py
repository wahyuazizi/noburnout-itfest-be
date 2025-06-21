import json
import os
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from app.models.transcript import TranscriptData
# from app.models.summary import SummaryData
# from app.models.study_plan import StudyPlanData
from app.config import settings

class StorageService:
    def __init__(self):
        self.transcripts: Dict[str, TranscriptData] = {}
        # self.summaries: Dict[str, SummaryData] = {}
        # self.study_plans: Dict[str, StudyPlanData] = {}

        # Memastikan storgge directory ada
        self._ensure_directories()

    def _ensure_directories(self):
        """buat storage directory jika belum ada"""
        directories = [
            f"{settings.storage_path}/transcripts",
            f"{settings.storage_path}/summaries",
            f"{settings.storage_path}/study_plans",
            f"{settings.storage_path}/pdfs",
            f"{settings.storage_path}/markdown",
        ]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    # Transkription Methods
    def save_transcript(self, transcript: TranscriptData) -> bool:
        """Simpan transkrip ke storage"""
        try:
            self.transcripts[transcript.id] = transcript

            # Simpan ke file
            file_path = f"{settings.storage_path}/transcripts/{transcript.id}.json"
            with open(file_path, 'w') as f:
                json.dump(transcript.model_dump(mode='json'), f, ensure_ascii=False, index=2)
            
            return True

        except Exception as e:
            return False

    def get_transcript(self, transcript_id: str) -> Optional[TranscriptData]:
        """Ambil transkrip dari memory atau file"""
        # Cek di memory
        if transcript_id in self.transcripts:
            return self.transcripts[transcript_id]

        # Cek di file
        try:
            file_path = f"{settings.storage_path}/transcripts/{transcript_id}.json"
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    transcript = TranscriptData(**data)
                    self.transcripts[transcript_id] = transcript
                    return transcript
        except Exception as e:
            return None

    def delete_transcript(self, transcript_id: str) -> bool:
        """Hapus transkrip dari memory dan file"""
        # Hapus dari memory
        try:
            if transcript_id in self.transcripts:
                del self.transcripts[transcript_id]

        # Hapus dari file
            file_path = f"{settings.storage_path}/transcripts/{transcript_id}.json"
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            return False
        
    def list_transcripts(self) -> List[TranscriptData]:
        """List semua transkrip yang ada di memory dan file"""
        transcript_dir = f"{settings.storage_path}/transcripts"
        if os.path.exists(transcript_dir):
            for filename in os.listdir(transcript_dir):
                if filename.endswith('.json'):
                    transcript_id = filename[:-5] # menghapus .json
                    if transcript_id not in self.transcripts:
                        self.get_transcript(transcript_id) # Load from file if not in memory
        return list(self.transcripts.values())
    
    def clean_old_files(self):
        """Bersihkan file"""
        cutoff_time = datetime.now() - timedelta(hours=settings.cleanup_after_hours)

        for transcript_id, transcript in list(self.transcripts.items()):
            if transcript.created_at < cutoff_time:
                self.delete_transcript(transcript_id)

# Global instance of StorageService
storage = StorageService()
