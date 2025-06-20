import json
import os
from typing import Dict, Optional, List
from app.models.transcript import TranscriptData
from app.models.summary import SummaryData
from app.models.study_plan import StudyPlanData
from app.config import settings

class StorageService:
    def __init__(self):
        self.transcripts: Dict[str, TranscriptData] = {}
        self.summaries: Dict[str, SummaryData] = {}
        self.study_plans: Dict[str, StudyPlanData] = {}

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


        