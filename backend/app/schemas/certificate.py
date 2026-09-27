from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel


class CertificateStatus(str, Enum):
    VALID = "Valid"
    REVOKED = "Revoked"


class CertificateCreate(BaseModel):
    inspection_id: int


class CertificateResponse(BaseModel):
    id: int
    organization_id: int
    battery_id: int
    inspection_id: int
    issued_by: int

    certificate_number: str
    issue_date: date
    status: CertificateStatus

    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
class CertificateVerificationResponse(BaseModel):
    certificate_valid: bool

    certificate_number: str
    certificate_status: str
    issue_date: date

    organization: str

    battery_serial: str
    manufacturer: str
    model: str

    inspection_id: int
    inspection_date: date

    inspector: str

    health_score: float
    health_status: str