from sqlalchemy import func,desc
from sqlalchemy.orm import Session

from backend.app.models.battery import Battery
from backend.app.models.inspection import Inspection
from backend.app.models.user import User
from backend.app.models.inspection import Inspection
from backend.app.models.battery import Battery


def get_dashboard_summary(
    db: Session,
    current_user: User,
):
    organization_id = current_user.organization_id

    total_batteries = (
        db.query(Battery)
        .filter(Battery.organization_id == organization_id)
        .count()
    )

    active_batteries = (
        db.query(Battery)
        .filter(
            Battery.organization_id == organization_id,
            Battery.status == "Active",
        )
        .count()
    )

    inactive_batteries = total_batteries - active_batteries

    total_inspections = (
        db.query(Inspection)
        .join(Battery)
        .filter(Battery.organization_id == organization_id)
        .count()
    )

    average_health_score = (
        db.query(func.avg(Inspection.health_score))
        .join(Battery)
        .filter(Battery.organization_id == organization_id)
        .scalar()
    )

    average_health_score = round(
        average_health_score or 0,
        2,
    )

    excellent_batteries = (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Battery.organization_id == organization_id,
            Inspection.health_status == "Excellent",
        )
        .count()
    )

    good_batteries = (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Battery.organization_id == organization_id,
            Inspection.health_status == "Good",
        )
        .count()
    )

    warning_batteries = (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Battery.organization_id == organization_id,
            Inspection.health_status == "Warning",
        )
        .count()
    )

    critical_batteries = (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Battery.organization_id == organization_id,
            Inspection.health_status == "Critical",
        )
        .count()
    )

    return {
        "total_batteries": total_batteries,
        "active_batteries": active_batteries,
        "inactive_batteries": inactive_batteries,
        "total_inspections": total_inspections,
        "average_health_score": average_health_score,
        "excellent_batteries": excellent_batteries,
        "good_batteries": good_batteries,
        "warning_batteries": warning_batteries,
        "critical_batteries": critical_batteries,
    }

def get_health_trend(
    db: Session,
    current_user: User,
):
    inspections = (
        db.query(Inspection, Battery.serial_number)
        .join(Battery)
        .filter(
            Battery.organization_id == current_user.organization_id
        )
        .order_by(Inspection.inspection_date.asc())
        .all()
    )

    return [
        {
            "inspection_date": inspection.inspection_date,
            "battery_serial": serial,
            "health_score": inspection.health_score,
            "health_status": inspection.health_status,
        }
        for inspection, serial in inspections
    ]
def get_recent_inspections(
    db: Session,
    current_user: User,
):
    inspections = (
        db.query(
            Inspection,
            Battery.serial_number,
            User.full_name,
        )
        .join(Battery)
        .join(User)
        .filter(
            Battery.organization_id == current_user.organization_id
        )
        .order_by(desc(Inspection.created_at))
        .limit(5)
        .all()
    )

    return [
        {
            "inspection_id": inspection.id,
            "battery_serial": serial,
            "inspector_name": inspector,
            "inspection_date": inspection.inspection_date,
            "health_score": inspection.health_score,
            "health_status": inspection.health_status,
        }
        for inspection, serial, inspector in inspections
    ]
def get_critical_batteries(
    db: Session,
    current_user: User,
):
    inspections = (
        db.query(Inspection, Battery)
        .join(Battery)
        .filter(
            Battery.organization_id == current_user.organization_id,
            Inspection.health_status == "Critical",
        )
        .order_by(desc(Inspection.health_score))
        .all()
    )

    return [
        {
            "battery_id": battery.id,
            "serial_number": battery.serial_number,
            "manufacturer": battery.manufacturer,
            "health_score": inspection.health_score,
            "health_status": inspection.health_status,
            "inspection_date": inspection.inspection_date,
        }
        for inspection, battery in inspections
    ]