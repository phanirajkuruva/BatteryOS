from pydantic import BaseModel
from datetime import date


class DashboardSummaryResponse(BaseModel):
    total_batteries: int
    active_batteries: int
    inactive_batteries: int

    total_inspections: int

    average_health_score: float

    excellent_batteries: int
    good_batteries: int
    warning_batteries: int
    critical_batteries: int

class HealthTrendItem(BaseModel):
    inspection_date: date
    battery_serial: str
    health_score: float
    health_status: str


class RecentInspectionItem(BaseModel):
    inspection_id: int
    battery_serial: str
    inspector_name: str
    inspection_date: date
    health_score: float
    health_status: str


class CriticalBatteryItem(BaseModel):
    battery_id: int
    serial_number: str
    manufacturer: str
    health_score: float
    health_status: str
    inspection_date: date