from sqlalchemy.orm import Session

from backend.app.models.battery import Battery
from backend.app.models.inspection import Inspection
from backend.app.models.user import User
from backend.app.utils.health_engine import calculate_health_score



def create_inspection(
    db: Session,
    inspection,
    current_user: User,
):
    """
    Create a new inspection for a battery that belongs
    to the current user's organization.
    """

    # Check battery belongs to logged-in user's organization
    battery = (
        db.query(Battery)
        .filter(
            Battery.id == inspection.battery_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )

    if battery is None:
        return None
    
    health_score, health_status = calculate_health_score(
    inspection.voltage,
    inspection.temperature,
    inspection.cycle_count,
)
    new_inspection = Inspection(
        battery_id=inspection.battery_id,
        inspector_id=current_user.id,
        inspection_date=inspection.inspection_date,
        health_score=health_score,
        health_status=health_status,
        temperature=inspection.temperature,
        voltage=inspection.voltage,
        cycle_count=inspection.cycle_count,
        remarks=inspection.remarks,
    )

    db.add(new_inspection)
    db.commit()
    db.refresh(new_inspection)

    return new_inspection

def get_all_inspections(
    db: Session,
    current_user: User,
):
    return (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Battery.organization_id == current_user.organization_id
        )
        .order_by(
            Inspection.inspection_date.desc()
        )
        .all()
    )

def get_inspection_by_id(
    db: Session,
    inspection_id: int,
    current_user: User,
):
    return (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Inspection.id == inspection_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )

def get_battery_inspections(
    db: Session,
    battery_id: int,
    current_user: User,
):
    return (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Inspection.battery_id == battery_id,
            Battery.organization_id == current_user.organization_id,
        )
        .order_by(
            Inspection.inspection_date.desc()
        )
        .all()
    )

def update_inspection(
    db: Session,
    inspection_id: int,
    inspection,
    current_user: User,
):
    
    existing_inspection = (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Inspection.id == inspection_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )

    if existing_inspection is None:
        return None

    health_score, health_status = calculate_health_score(
    inspection.voltage,
    inspection.temperature,
    inspection.cycle_count,
)
    
    existing_inspection.inspection_date = inspection.inspection_date
    existing_inspection.health_score = health_score
    existing_inspection.health_status = health_status
    existing_inspection.temperature = inspection.temperature
    existing_inspection.voltage = inspection.voltage
    existing_inspection.cycle_count = inspection.cycle_count
    existing_inspection.remarks = inspection.remarks

    db.commit()
    db.refresh(existing_inspection)

    return existing_inspection

def delete_inspection(
    db: Session,
    inspection_id: int,
    current_user: User,
):
    inspection = (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Inspection.id == inspection_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )

    if inspection is None:
        return False

    db.delete(inspection)
    db.commit()

    return True