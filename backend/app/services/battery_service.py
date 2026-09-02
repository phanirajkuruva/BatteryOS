from sqlalchemy.orm import Session

from backend.app.models import Battery as BatteryModel
from backend.app.schemas.battery import BatteryCreate
from backend.app.models.organization import Organization
from backend.app.models.battery import Battery
from backend.app.models.user import User
from sqlalchemy.orm import joinedload


def get_all_batteries(db: Session,current_user: User):
    return db.query(Battery).filter(
        Battery.organization_id == current_user.organization_id
    ).all()


def get_battery_by_id(db: Session, battery_id: int,current_user: User):
    return db.query(Battery).filter(
        Battery.id == battery_id,
        Battery.organization_id == current_user.organization_id
    ).first()


def create_battery(db: Session, battery: BatteryCreate,current_user: User):
    # organization = db.query(Organization).filter(
    #     Organization.id == battery.organization_id
    # ).first()

    # if organization is None:
    #     return None
    new_battery = BatteryModel(
         organization_id=current_user.organization_id,
        serial_number=battery.serial_number,
        manufacturer=battery.manufacturer,
        model=battery.model,
        chemistry=battery.chemistry,
        capacity=battery.capacity,
        voltage=battery.voltage,
        status=battery.status.value,
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
    battery: BatteryCreate,
    current_user: User
):
        # Check whether battery exists
    existing_battery = db.query(Battery).filter(
        Battery.id == battery_id,
        Battery.organization_id == current_user.organization_id,
    ).first()

    if existing_battery is None:
        return None
    #     # Check whether organization exists
    # organization = db.query(Organization).filter(
    #     Organization.id == battery.organization_id
    # ).first()

    # if organization is None:
    #     return None

   # existing_battery.organization_id = battery.organization_id
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


def delete_battery(
    db: Session,
    battery_id: int,
    current_user: User,
):
    battery = (
        db.query(Battery)
        .filter(
            Battery.id == battery_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )

    if battery is None:
        return False

    db.delete(battery)
    db.commit()

    return True
def get_batteries_by_organization(
    db: Session,
    organization_id: int
):
    return db.query(Battery).filter(
        Battery.organization_id == organization_id
    ).all()

def get_battery_with_history(
    db: Session,
    battery_id: int,
    current_user: User,
):
    battery = (
        db.query(Battery)
        .options(joinedload(Battery.inspections))
        .filter(
            Battery.id == battery_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )

    return battery