from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AudioFile(BaseModel):
    file_name: Optional[str] = None
    transcription: Optional[str] = None
    path: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    transcription_json: Optional[str] = None
