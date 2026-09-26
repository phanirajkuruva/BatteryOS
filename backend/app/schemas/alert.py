from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class AlertSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class AlertType(str, Enum):
    LOW_HEALTH = "LOW_HEALTH"
    HIGH_TEMPERATURE = "HIGH_TEMPERATURE"
    WARRANTY_EXPIRY = "WARRANTY_EXPIRY"
    OVERDUE_MAINTENANCE = "OVERDUE_MAINTENANCE"


class AlertResponse(BaseModel):
    id: int
    organization_id: int
    battery_id: int

    alert_type: AlertType
    severity: AlertSeverity

    title: str
    message: str

    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class AlertReadUpdate(BaseModel):
    is_read: bool = True


class AlertDashboardSummaryResponse(BaseModel):
    total_alerts: int
    unread_alerts: int
    critical_alerts: int
    high_alerts: int