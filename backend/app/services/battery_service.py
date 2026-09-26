from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import date, timedelta
from sqlalchemy import func
from backend.app.models import Battery as BatteryModel
from backend.app.schemas.battery import BatteryCreate, BatteryUpdate
from backend.app.models.organization import Organization
from backend.app.models.battery import Battery
from backend.app.models.user import User
from sqlalchemy.orm import joinedload

VALID_LIFECYCLE_STATUSES = {
    "Active",
    "Maintenance",
    "Retired",
    "Recycled",
}

VALID_LIFECYCLE_TRANSITIONS = {
    "Active": ["Maintenance", "Retired"],
    "Maintenance": ["Active", "Retired"],
    "Retired": ["Recycled"],
    "Recycled": [],
}
def get_all_batteries(db: Session,current_user: User):
    return db.query(Battery).filter(
        Battery.organization_id == current_user.organization_id
    ).all()


def get_battery_by_id(db: Session, battery_id: int,current_user: User):
    return db.query(Battery).filter(
        Battery.id == battery_id,
        Battery.organization_id == current_user.organization_id
    ).first()


def create_battery(
    db: Session,
    battery: BatteryCreate,
    current_user: User,
):
    # Validate warranty dates first
    if (
        battery.warranty_start_date
        and battery.warranty_end_date
        and battery.warranty_end_date < battery.warranty_start_date
    ):
        raise HTTPException(
            status_code=400,
            detail="Warranty end date cannot be before warranty start date.",
        )

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
        installation_date=battery.installation_date,

        # NEW FIELDS
        purchase_date=battery.purchase_date,
        warranty_start_date=battery.warranty_start_date,
        warranty_end_date=battery.warranty_end_date,
    )

    db.add(new_battery)
    db.commit()
    db.refresh(new_battery)

    return new_battery

def update_battery(
    db: Session,
    battery_id: int,
    battery: BatteryUpdate,
    current_user: User,
):
    existing_battery = (
        db.query(BatteryModel)
        .filter(
            BatteryModel.id == battery_id,
            BatteryModel.organization_id == current_user.organization_id,
        )
        .first()
    )

    if existing_battery is None:
        return None

    # Get only fields sent in request
    update_data = battery.model_dump(exclude_unset=True)

    # Validate warranty dates
    start_date = update_data.get(
        "warranty_start_date",
        existing_battery.warranty_start_date,
    )

    end_date = update_data.get(
        "warranty_end_date",
        existing_battery.warranty_end_date,
    )

    if (
        start_date
        and end_date
        and end_date < start_date
    ):
        raise HTTPException(
            status_code=400,
            detail="Warranty end date cannot be before warranty start date.",
        )

    # Update only provided fields
    for key, value in update_data.items():
        if key == "status" and value is not None:
            value = value.value
        setattr(existing_battery, key, value)

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

def update_lifecycle_status(
    db: Session,
    battery_id: int,
    lifecycle_status: str,
    retired_date,
    retirement_reason,
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
        return None

    # Validate lifecycle value
    if lifecycle_status not in VALID_LIFECYCLE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid lifecycle status.",
        )

    current_status = battery.lifecycle_status

    if lifecycle_status == current_status:
        raise HTTPException(
            status_code=400,
            detail="Battery already has this lifecycle status.",
        )

    allowed_statuses = VALID_LIFECYCLE_TRANSITIONS[current_status]

    if lifecycle_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change lifecycle from '{current_status}' to '{lifecycle_status}'.",
        )

    # Retirement validations
    if lifecycle_status == "Retired":
        if retired_date is None:
            raise HTTPException(
                status_code=400,
                detail="Retired date is required.",
            )

        if retirement_reason is None:
            raise HTTPException(
                status_code=400,
                detail="Retirement reason is required.",
            )

        battery.retired_date = retired_date
        battery.retirement_reason = retirement_reason

    battery.lifecycle_status = lifecycle_status

    db.commit()
    db.refresh(battery)

    return battery
def get_battery_dashboard_summary(
    db: Session,
    current_user: User,
):
    batteries = (
        db.query(BatteryModel)
        .filter(
            BatteryModel.organization_id == current_user.organization_id,
        )
    )

    return {
        "total_batteries": batteries.count(),
        "active": batteries.filter(
            BatteryModel.lifecycle_status == "Active"
        ).count(),
        "maintenance": batteries.filter(
            BatteryModel.lifecycle_status == "Maintenance"
        ).count(),
        "retired": batteries.filter(
            BatteryModel.lifecycle_status == "Retired"
        ).count(),
        "recycled": batteries.filter(
            BatteryModel.lifecycle_status == "Recycled"
        ).count(),
    }
def get_warranty_expiring_batteries(
    db: Session,
    current_user: User,
):
    today = date.today()
    next_30_days = today + timedelta(days=30)

    return (
        db.query(BatteryModel)
        .filter(
            BatteryModel.organization_id == current_user.organization_id,
            BatteryModel.warranty_end_date.is_not(None),
            BatteryModel.warranty_end_date >= today,
            BatteryModel.warranty_end_date <= next_30_days,
            BatteryModel.lifecycle_status != "Retired",
            BatteryModel.lifecycle_status != "Recycled",
        )
        .order_by(BatteryModel.warranty_end_date)
        .all()
    )
def get_expired_warranty_batteries(
    db: Session,
    current_user: User,
):
    today = date.today()

    return (
        db.query(BatteryModel)
        .filter(
            BatteryModel.organization_id == current_user.organization_id,
            BatteryModel.warranty_end_date.is_not(None),
            BatteryModel.warranty_end_date < today,
            BatteryModel.lifecycle_status != "Retired",
            BatteryModel.lifecycle_status != "Recycled",
        )
        .order_by(BatteryModel.warranty_end_date)
        .all()
    )
def get_warranty_summary(
    db: Session,
    current_user: User,
):
    today = date.today()
    next_30_days = today + timedelta(days=30)

    batteries = (
        db.query(BatteryModel)
        .filter(
            BatteryModel.organization_id == current_user.organization_id,
        )
    )

    return {
        "under_warranty": batteries.filter(
            BatteryModel.warranty_end_date >= today,
        ).count(),

        "expired_warranty": batteries.filter(
            BatteryModel.warranty_end_date < today,
        ).count(),

        "expiring_in_30_days": batteries.filter(
            BatteryModel.warranty_end_date >= today,
            BatteryModel.warranty_end_date <= next_30_days,
        ).count(),
    }
def get_lifecycle_summary(
    db: Session,
    current_user: User,
):
    batteries = (
        db.query(BatteryModel)
        .filter(
            BatteryModel.organization_id == current_user.organization_id,
        )
    )

    return {
        "active": batteries.filter(
            BatteryModel.lifecycle_status == "Active",
        ).count(),

        "maintenance": batteries.filter(
            BatteryModel.lifecycle_status == "Maintenance",
        ).count(),

        "retired": batteries.filter(
            BatteryModel.lifecycle_status == "Retired",
        ).count(),

        "recycled": batteries.filter(
            BatteryModel.lifecycle_status == "Recycled",
        ).count(),
    }