from datetime import datetime
from pydantic import BaseModel


class AttachmentResponse(BaseModel):
    id: int

    inspection_id: int

    original_name: str
    stored_name: str

    file_type: str
    file_path: str
    file_url: str 

    uploaded_by: int

    created_at: datetime

    model_config = {
        "from_attributes": True
    }