from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False
    )

    full_name = Column(String(100), nullable=False)

    email = Column(
        String(150),
        nullable=False,
        unique=True,
        index=True
    )

    password_hash = Column(String(255), nullable=False)

    role = Column(String(30), nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    organization = relationship(
        "Organization",
        back_populates="users"
    )

    inspections = relationship(
    "Inspection",
    back_populates="inspector",
    )
    attachments = relationship(
    "Attachment",
    back_populates="uploader",
    )
    maintenance_records = relationship(
    "Maintenance",
    back_populates="technician",
    )   
    certificates = relationship(
    "Certificate",
    back_populates="issuer",
    )