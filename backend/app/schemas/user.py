from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRole(str, Enum):
    OWNER = "Owner"
    ADMIN = "Admin"
    TECHNICIAN = "Technician"
    VIEWER = "Viewer"
    AUDITOR = "Auditor"


class UserCreate(BaseModel):
    organization_id: int = Field(gt=0)

    full_name: str = Field(min_length=3, max_length=100)

    email: EmailStr

    password: str = Field(min_length=8)

    role: UserRole


class UserResponse(BaseModel):
    id: int
    organization_id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
class UserRoleUpdate(BaseModel):
    role: UserRole


class UserStatusUpdate(BaseModel):
    is_active: bool