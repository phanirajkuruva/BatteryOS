from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from datetime import date, timedelta
from backend.app.models.alert import Alert
from backend.app.models.battery import Battery
from backend.app.models.inspection import Inspection
from backend.app.models.maintenance import Maintenance
from backend.app.models.user import User


def get_dashboard_summary(
    db: Session,
    current_user: User,
):
    organization_id = current_user.organization_id

    # -------------------------------------------------
    # BATTERY COUNTS
    # -------------------------------------------------

    total_batteries = (
        db.query(Battery)
        .filter(
            Battery.organization_id == organization_id
        )
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

    inactive_batteries = (
        db.query(Battery)
        .filter(
            Battery.organization_id == organization_id,
            Battery.status == "Inactive",
        )
        .count()
    )

    maintenance_batteries = (
        db.query(Battery)
        .filter(
            Battery.organization_id == organization_id,
            Battery.status == "Maintenance",
        )
        .count()
    )

    retired_batteries = (
        db.query(Battery)
        .filter(
            Battery.organization_id == organization_id,
            Battery.lifecycle_status == "Retired",
        )
        .count()
    )

    # -------------------------------------------------
    # INSPECTION COUNTS
    # -------------------------------------------------

    total_inspections = (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Battery.organization_id == organization_id
        )
        .count()
    )

    average_health_score = (
        db.query(
            func.avg(Inspection.health_score)
        )
        .join(Battery)
        .filter(
            Battery.organization_id == organization_id
        )
        .scalar()
    )

    average_health_score = round(
        float(average_health_score or 0),
        2,
    )

    # -------------------------------------------------
    # LATEST INSPECTION FOR EACH BATTERY
    # -------------------------------------------------

    latest_inspection_subquery = (
        db.query(
            Inspection.battery_id.label("battery_id"),
            func.max(Inspection.id).label("latest_inspection_id"),
        )
        .join(Battery)
        .filter(
            Battery.organization_id == organization_id
        )
        .group_by(Inspection.battery_id)
        .subquery()
    )

    latest_inspections = (
        db.query(Inspection)
        .join(
            latest_inspection_subquery,
            Inspection.id
            == latest_inspection_subquery.c.latest_inspection_id,
        )
        .all()
    )

    # -------------------------------------------------
    # CURRENT HEALTH DISTRIBUTION
    # -------------------------------------------------

    excellent_batteries = 0
    good_batteries = 0
    warning_batteries = 0
    critical_batteries = 0

    for inspection in latest_inspections:

        if inspection.health_status == "Excellent":
            excellent_batteries += 1

        elif inspection.health_status == "Good":
            good_batteries += 1

        elif inspection.health_status == "Warning":
            warning_batteries += 1

        elif inspection.health_status == "Critical":
            critical_batteries += 1

    # -------------------------------------------------
    # ACTIVE ALERTS
    # -------------------------------------------------

    active_alerts = (
        db.query(Alert)
        .join(Battery)
        .filter(
            Battery.organization_id == organization_id,
            Alert.is_read.is_(False),
        )
        .count()
    )

    # -------------------------------------------------
    # SCHEDULED MAINTENANCE
    # -------------------------------------------------

    scheduled_maintenance = (
        db.query(Maintenance)
        .join(Battery)
        .filter(
            Battery.organization_id == organization_id,
            Maintenance.status == "Scheduled",
        )
        .count()
    )

    return {
        "total_batteries": total_batteries,
        "active_batteries": active_batteries,
        "inactive_batteries": inactive_batteries,

        "retired_batteries": retired_batteries,
        "maintenance_batteries": maintenance_batteries,

        "total_inspections": total_inspections,
        "average_health_score": average_health_score,

        "excellent_batteries": excellent_batteries,
        "good_batteries": good_batteries,
        "warning_batteries": warning_batteries,
        "critical_batteries": critical_batteries,

        "active_alerts": active_alerts,
        "scheduled_maintenance": scheduled_maintenance,
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
    organization_id = current_user.organization_id

    latest_inspection_subquery = (
        db.query(
            Inspection.battery_id.label("battery_id"),
            func.max(Inspection.id).label("latest_inspection_id"),
        )
        .join(Battery)
        .filter(
            Battery.organization_id == organization_id
        )
        .group_by(Inspection.battery_id)
        .subquery()
    )

    inspections = (
        db.query(
            Inspection,
            Battery,
        )
        .join(
            latest_inspection_subquery,
            Inspection.id
            == latest_inspection_subquery.c.latest_inspection_id,
        )
        .join(
            Battery,
            Battery.id == Inspection.battery_id,
        )
        .filter(
            Battery.organization_id == organization_id,
            Inspection.health_status == "Critical",
        )
        .order_by(
            Inspection.health_score.asc()
        )
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

def get_upcoming_maintenance(
    db: Session,
    current_user: User,
):
    """
    Return scheduled maintenance for the next 30 days
    for batteries belonging to the current organization.
    """

    today = date.today()
    end_date = today + timedelta(days=30)

    records = (
        db.query(
            Maintenance,
            Battery.serial_number,
            User.full_name,
        )
        .join(
            Battery,
            Battery.id == Maintenance.battery_id,
        )
        .join(
            User,
            User.id == Maintenance.assigned_to,
        )
        .filter(
            Battery.organization_id
            == current_user.organization_id,

            Maintenance.status == "Scheduled",

            Maintenance.scheduled_date >= today,

            Maintenance.scheduled_date <= end_date,
        )
        .order_by(
            Maintenance.scheduled_date.asc()
        )
        .all()
    )

    return [
        {
            "maintenance_id": maintenance.id,
            "battery_id": maintenance.battery_id,
            "battery_serial": serial_number,
            "maintenance_type": maintenance.maintenance_type,
            "scheduled_date": maintenance.scheduled_date,
            "assigned_to_name": assigned_to_name,
            "status": maintenance.status,
        }
        for maintenance, serial_number, assigned_to_name in records
    ]

def get_expiring_warranties(
    db: Session,
    current_user: User,
):
    """
    Return batteries whose warranty expires within
    the next 30 days.
    """

    today = date.today()
    end_date = today + timedelta(days=30)

    batteries = (
        db.query(Battery)
        .filter(
            Battery.organization_id
            == current_user.organization_id,

            Battery.warranty_end_date.isnot(None),

            Battery.warranty_end_date >= today,

            Battery.warranty_end_date <= end_date,

            Battery.lifecycle_status != "Retired",
        )
        .order_by(
            Battery.warranty_end_date.asc()
        )
        .all()
    )

    return [
        {
            "battery_id": battery.id,
            "serial_number": battery.serial_number,
            "manufacturer": battery.manufacturer,
            "warranty_end_date": battery.warranty_end_date,
            "days_remaining": (
                battery.warranty_end_date - today
            ).days,
        }
        for battery in batteries
    ]
def get_recent_alerts(
    db: Session,
    current_user: User,
):
    """
    Return the 5 most recent alerts belonging
    to the current user's organization.
    """

    alerts = (
        db.query(
            Alert,
            Battery.serial_number,
        )
        .join(
            Battery,
            Battery.id == Alert.battery_id,
        )
        .filter(
            Battery.organization_id
            == current_user.organization_id
        )
        .order_by(
            Alert.created_at.desc()
        )
        .limit(5)
        .all()
    )

    return [
        {
            "alert_id": alert.id,
            "battery_id": alert.battery_id,
            "battery_serial": serial_number,
            "alert_type": alert.alert_type,
            "severity": alert.severity,
            "message": alert.message,
            "is_read": alert.is_read,
            "created_at": alert.created_at,
        }
        for alert, serial_number in alerts
    ]