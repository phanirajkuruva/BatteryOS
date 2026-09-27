from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.models.base import Base


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False,
    )

    battery_id = Column(
        Integer,
        ForeignKey("batteries.id"),
        nullable=False,
    )
    inspection_id = Column(
    Integer,
    ForeignKey("inspections.id"),
    nullable=False,
    )

    issued_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    certificate_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
    )

    issue_date = Column(
        Date,
        nullable=False,
    )

    status = Column(
        String(20),
        nullable=False,
        default="Valid",
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    battery = relationship(
        "Battery",
        back_populates="certificates",
    )
    inspection = relationship(
        "Inspection",
        back_populates="certificates",
    )
    organization = relationship(
        "Organization",
        back_populates="certificates",
    )

    issuer = relationship(
        "User",
        back_populates="certificates",
    )