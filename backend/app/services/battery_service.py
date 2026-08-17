from sqlalchemy.orm import Session

from backend.app.models import Battery as BatteryModel
from backend.app.schemas.battery import BatteryCreate


def get_all_batteries(db: Session):
    return db.query(BatteryModel).all()


def get_battery_by_id(db: Session, battery_id: int):
    return db.query(BatteryModel).filter(
        BatteryModel.id == battery_id
    ).first()


def create_battery(db: Session, battery: BatteryCreate):
    new_battery = BatteryModel(
        serial_number=battery.serial_number,
        manufacturer=battery.manufacturer,
        model=battery.model,
        chemistry=battery.chemistry,
        capacity=battery.capacity,
        voltage=battery.voltage,
        status=battery.status,
        manufacturing_date=battery.manufacturing_date,
        installation_date=battery.installation_date
    )

    db.add(new_battery)
    db.commit()
    db.refresh(new_battery)

    return new_battery


def update_battery(
    db: Session,
    battery_id: int,
    battery: BatteryCreate
):
    existing_battery = get_battery_by_id(db, battery_id)

    if existing_battery is None:
        return None

    existing_battery.serial_number = battery.serial_number
    existing_battery.manufacturer = battery.manufacturer
    existing_battery.model = battery.model
    existing_battery.chemistry = battery.chemistry
    existing_battery.capacity = battery.capacity
    existing_battery.voltage = battery.voltage
    existing_battery.status = battery.status
    existing_battery.manufacturing_date = battery.manufacturing_date
    existing_battery.installation_date = battery.installation_date

    db.commit()
    db.refresh(existing_battery)

    return existing_battery


def delete_battery(db: Session, battery_id: int):
    existing_battery = get_battery_by_id(db, battery_id)

    if existing_battery is None:
        return False

    db.delete(existing_battery)
    db.commit()

    return True