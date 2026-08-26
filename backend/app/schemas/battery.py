from datetime import date
from enum import Enum

from pydantic import BaseModel, Field


class BatteryStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    MAINTENANCE = "Maintenance"


class BatteryCreate(BaseModel):
    #organization_id: int = Field(gt=0)
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
    capacity: float = Field(
        gt=0
    )
    voltage: float = Field(
        gt=0
    )
    status: BatteryStatus
    manufacturing_date: date
    installation_date: date | None = None


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
    installation_date: date | None = None

    class Config:
        from_attributes = True