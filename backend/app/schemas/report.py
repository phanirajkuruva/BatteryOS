from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class ReportInspectionResponse(BaseModel):
    id: int
    inspection_date: date
    health_score: float
    health_status: str
    temperature: float
    voltage: float
    cycle_count: int
    remarks: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class ReportMaintenanceResponse(BaseModel):
    id: int
    maintenance_type: str
    status: str
    scheduled_date: date
    completed_date: Optional[date] = None
    cost: Optional[float] = None
    notes: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class BatteryHealthReportResponse(BaseModel):
    battery_id: int
    serial_number: str
    manufacturer: str
    model: str
    chemistry: str

    capacity: float
    rated_voltage: float

    operational_status: str
    lifecycle_status: str

    manufacturing_date: date
    installation_date: Optional[date] = None

    purchase_date: Optional[date] = None
    warranty_start_date: Optional[date] = None
    warranty_end_date: Optional[date] = None

    latest_health_score: Optional[float] = None
    latest_health_status: Optional[str] = None

    total_inspections: int
    total_maintenance_records: int

    inspections: list[ReportInspectionResponse]
    maintenance_records: list[ReportMaintenanceResponse]

    generated_at: datetime