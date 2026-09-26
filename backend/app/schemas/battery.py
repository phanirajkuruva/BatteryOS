from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, func
from backend.app.schemas.inspection import InspectionResponse


class BatteryStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    MAINTENANCE = "Maintenance"


# NEW: Lifecycle enum
class BatteryLifecycleStatus(str, Enum):
    ACTIVE = "Active"
    MAINTENANCE = "Maintenance"
    RETIRED = "Retired"
    RECYCLED = "Recycled"


class BatteryCreate(BaseModel):
    serial_number: str = Field(
        min_length=3,
        max_length=100
    )
    manufacturer: str = Field(
        min_length=2,
        max_length=100
    )
    model: str = Field(
        min_length=2,
        max_length=100
    )
    chemistry: str = Field(
        min_length=2,
        max_length=50
    )
    capacity: float = Field(gt=0)
    voltage: float = Field(gt=0)

    status: BatteryStatus

    manufacturing_date: date
    installation_date: Optional[date] = None
    created_at: Optional[datetime] = None
    # NEW: Warranty fields
    purchase_date: Optional[date] = None
    warranty_start_date: Optional[date] = None
    warranty_end_date: Optional[date] = None


class BatteryUpdate(BaseModel):
    serial_number: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=100
    )

    manufacturer: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    model: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    chemistry: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50
    )

    capacity: Optional[float] = Field(
        default=None,
        gt=0
    )

    voltage: Optional[float] = Field(
        default=None,
        gt=0
    )

    status: Optional[BatteryStatus] = None

    manufacturing_date: Optional[date] = None
    installation_date: Optional[date] = None

    # NEW: Warranty fields
    purchase_date: Optional[date] = None
    warranty_start_date: Optional[date] = None
    warranty_end_date: Optional[date] = None


class BatteryResponse(BaseModel):
    id: int
    organization_id: int

    serial_number: str
    manufacturer: str
    model: str
    chemistry: str
    capacity: float
    voltage: float

    status: BatteryStatus

    manufacturing_date: date
    installation_date: Optional[date]

    # NEW: Warranty fields
    purchase_date: Optional[date]
    warranty_start_date: Optional[date]
    warranty_end_date: Optional[date]

    # NEW: Lifecycle fields
    lifecycle_status: BatteryLifecycleStatus
    retired_date: Optional[date]
    retirement_reason: Optional[str]

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class BatteryWithInspectionsResponse(BatteryResponse):
    inspections: list[InspectionResponse] = []

    model_config = {
        "from_attributes": True
    }
class BatteryLifecycleUpdate(BaseModel):
    lifecycle_status: BatteryLifecycleStatus

    retired_date: Optional[date] = None

    retirement_reason: Optional[str] = Field(
        default=None,
        max_length=255
    )
class BatteryDashboardSummaryResponse(BaseModel):
    total_batteries: int
    active: int
    maintenance: int
    retired: int
    recycled: int


class WarrantySummaryResponse(BaseModel):
    under_warranty: int
    expired_warranty: int
    expiring_in_30_days: int


class LifecycleSummaryResponse(BaseModel):
    active: int
    maintenance: int
    retired: int
    recycled: int

