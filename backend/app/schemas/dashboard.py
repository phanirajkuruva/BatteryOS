from datetime import date,datetime

from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    total_batteries: int
    active_batteries: int
    inactive_batteries: int

    retired_batteries: int
    maintenance_batteries: int

    total_inspections: int
    average_health_score: float

    excellent_batteries: int
    good_batteries: int
    warning_batteries: int
    critical_batteries: int

    active_alerts: int
    scheduled_maintenance: int


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

class UpcomingMaintenanceItem(BaseModel):
    maintenance_id: int
    battery_id: int
    battery_serial: str
    maintenance_type: str
    scheduled_date: date
    assigned_to_name: str
    status: str


class WarrantyExpiringItem(BaseModel):
    battery_id: int
    serial_number: str
    manufacturer: str
    warranty_end_date: date
    days_remaining: int

class RecentAlertItem(BaseModel):
    alert_id: int
    battery_id: int
    battery_serial: str

    alert_type: str
    severity: str
    message: str

    is_read: bool
    created_at: datetime