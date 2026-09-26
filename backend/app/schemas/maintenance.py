from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# -----------------------------
# Create Maintenance
# -----------------------------
class MaintenanceCreate(BaseModel):
    battery_id: int

    assigned_to: int

    maintenance_type: str = Field(
        min_length=3,
        max_length=50,
    )

    scheduled_date: date

    cost: Optional[float] = None

    notes: Optional[str] = Field(
        default=None,
        max_length=500,
    )


# -----------------------------
# Update Maintenance
# -----------------------------
class MaintenanceUpdate(BaseModel):
    assigned_to: Optional[int] = None

    maintenance_type: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    scheduled_date: Optional[date] = None

    completed_date: Optional[date] = None

    status: Optional[str] = None

    cost: Optional[float] = None

    notes: Optional[str] = Field(
        default=None,
        max_length=500,
    )


# -----------------------------
# Response Model
# -----------------------------
class MaintenanceResponse(BaseModel):
    id: int

    battery_id: int

    assigned_to: int

    maintenance_type: str

    status: str

    scheduled_date: date

    completed_date: Optional[date]

    cost: Optional[float]

    notes: Optional[str]

    created_at: datetime

    model_config = {
        "from_attributes": True
    }
class MaintenanceStatusUpdate(BaseModel):
    status: str

    completed_date: Optional[date] = None

class MaintenanceSummaryResponse(BaseModel):
    total_jobs: int
    scheduled: int
    in_progress: int
    completed: int


class CostSummaryResponse(BaseModel):
    total_cost: float
    total_completed_jobs: int


class BatteryCostResponse(BaseModel):
    battery_id: int
    serial_number: str
    total_cost: float