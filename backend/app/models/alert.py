from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from backend.app.models.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

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

    alert_type = Column(
        String(50),
        nullable=False,
    )

    severity = Column(
        String(20),
        nullable=False,
    )

    title = Column(
        String(150),
        nullable=False,
    )

    message = Column(
        String(500),
        nullable=False,
    )

    is_read = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    battery = relationship(
        "Battery",
        back_populates="alerts",
    )

    organization = relationship(
        "Organization",
        back_populates="alerts",
    )