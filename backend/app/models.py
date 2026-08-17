from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Battery(Base):
    __tablename__ = "batteries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    serial_number: Mapped[str] = mapped_column(String(100), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)