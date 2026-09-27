from sqlalchemy import (Column, Integer, String, Float, Date, ForeignKey, DateTime)
from sqlalchemy.orm import relationship
from backend.app.models.base import Base
from sqlalchemy import Date
from sqlalchemy.sql import func


class Battery(Base):
    __tablename__ = "batteries"

    id = Column(Integer, primary_key=True, index=True)
    organization_id=Column(Integer, ForeignKey("organizations.id"),nullable=False)
    purchase_date = Column(Date,nullable=True,)
    warranty_start_date = Column(Date,nullable=True,)
    warranty_end_date = Column(Date,nullable=True,)
    lifecycle_status = Column(String(20),nullable=False,default="Active",)
    retired_date = Column(Date, nullable=True,)
    retirement_reason = Column(String(255),nullable=True,)
    serial_number = Column(String(100), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    chemistry = Column(String(50), nullable=False)
    capacity = Column(Float, nullable=False)
    voltage = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    manufacturing_date = Column(Date, nullable=False)
    installation_date = Column(Date, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    organization=relationship("Organization",back_populates="batteries")

    inspections = relationship(
    "Inspection",
    back_populates="battery",
    cascade="all, delete-orphan",
    )
    maintenance_records = relationship(
    "Maintenance",
    back_populates="battery",
    cascade="all, delete",
    )
    alerts = relationship(
    "Alert",
    back_populates="battery",
    cascade="all, delete-orphan",
    )
    certificates = relationship(
    "Certificate",
    back_populates="battery",
    cascade="all, delete-orphan",
    )