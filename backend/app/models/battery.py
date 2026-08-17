from sqlalchemy import Column, Integer, String, Float, Date
from backend.app.models.base import Base


class Battery(Base):
    __tablename__ = "batteries"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String(100), nullable=False)
    manufacturer = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    chemistry = Column(String(50), nullable=False)
    capacity = Column(Float, nullable=False)
    voltage = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    manufacturing_date = Column(Date, nullable=False)
    installation_date = Column(Date, nullable=True)