from datetime import date, datetime

from pydantic import BaseModel, Field


class InspectionCreate(BaseModel):
    battery_id: int

    inspection_date: date

    temperature: float

    voltage: float

    cycle_count: int = Field(ge=0)

    remarks: str | None = None


class InspectionResponse(BaseModel):
    id: int

    battery_id: int

    inspector_id: int

    inspection_date: date

    health_score: float

    health_status: str

    temperature: float

    voltage: float

    cycle_count: int

    remarks: str | None

    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class InspectionUpdate(BaseModel):
    inspection_date: date

    temperature: float

    voltage: float

    cycle_count: int = Field(ge=0)

    remarks: str | None = None