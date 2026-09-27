from sqlalchemy import Column, Integer, Float, Date, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.models.base import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)

    battery_id = Column(
        Integer,
        ForeignKey("batteries.id"),
        nullable=False,
    )

    inspector_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    inspection_date = Column(Date, nullable=False)
    health_score = Column(Float, nullable=False)
    health_status = Column(String(20), nullable=False,)
    temperature = Column(Float, nullable=False)
    voltage = Column(Float, nullable=False)
    cycle_count = Column(Integer, nullable=False)
    remarks = Column(String(500), nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    battery = relationship(
        "Battery",
        back_populates="inspections",
    )

    inspector = relationship(
        "User",
        back_populates="inspections",
    )

    attachments = relationship(
    "Attachment",
    back_populates="inspection",
    cascade="all, delete",
    )
    certificates = relationship(
    "Certificate",
    back_populates="inspection",
    )