from typing import Optional
from pydantic import BaseModel


class ProgressStatus(BaseModel):
    file_id: Optional[str] = None
    status: Optional[str] = None
