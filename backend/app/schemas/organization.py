from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)

    email: EmailStr

    phone: str = Field(min_length=10, max_length=20)

    address: str = Field(min_length=5, max_length=255)

    country: str = Field(min_length=2, max_length=100)


class OrganizationResponse(BaseModel):
    id: int

    name: str
    email: EmailStr
    phone: str
    address: str
    country: str

    created_at: datetime

    class Config:
        from_attributes = True