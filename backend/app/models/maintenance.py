from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.models.base import Base


class Maintenance(Base):
    __tablename__ = "maintenance"

    id = Column(Integer, primary_key=True, index=True)

    battery_id = Column(
        Integer,
        ForeignKey("batteries.id"),
        nullable=False,
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    maintenance_type = Column(
        String(50),
        nullable=False,
    )

    status = Column(
        String(20),
        nullable=False,
        default="Scheduled",
    )

    scheduled_date = Column(
        Date,
        nullable=False,
    )

    completed_date = Column(
        Date,
        nullable=True,
    )

    cost = Column(
        Float,
        nullable=True,
    )

    notes = Column(
        String(500),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    battery = relationship(
        "Battery",
        back_populates="maintenance_records",
    )

    technician = relationship(
        "User",
        back_populates="maintenance_records",
    )