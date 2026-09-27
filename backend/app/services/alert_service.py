from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.alert import Alert
from backend.app.models.inspection import Inspection
from backend.app.models.battery import Battery
from backend.app.models.user import User
from backend.app.models.maintenance import Maintenance

def get_all_alerts(
    db: Session,
    current_user: User,
):
    return (
        db.query(Alert)
        .filter(
            Alert.organization_id == current_user.organization_id,
        )
        .order_by(Alert.created_at.desc())
        .all()
    )


def get_unread_alerts(
    db: Session,
    current_user: User,
):
    return (
        db.query(Alert)
        .filter(
            Alert.organization_id == current_user.organization_id,
            Alert.is_read.is_(False),
        )
        .order_by(Alert.created_at.desc())
        .all()
    )


def mark_alert_as_read(
    db: Session,
    alert_id: int,
    current_user: User,
):
    alert = (
        db.query(Alert)
        .filter(
            Alert.id == alert_id,
            Alert.organization_id == current_user.organization_id,
        )
        .first()
    )

    if alert is None:
        return None

    alert.is_read = True

    db.commit()
    db.refresh(alert)

    return alert


def get_alert_dashboard_summary(
    db: Session,
    current_user: User,
):
    alerts = (
        db.query(Alert)
        .filter(
            Alert.organization_id == current_user.organization_id,
        )
    )

    return {
        "total_alerts": alerts.count(),
        "unread_alerts": alerts.filter(
            Alert.is_read.is_(False)
        ).count(),
        "critical_alerts": alerts.filter(
            Alert.severity == "Critical"
        ).count(),
        "high_alerts": alerts.filter(
            Alert.severity == "High"
        ).count(),
    }
def alert_exists(
    db: Session,
    battery_id: int,
    alert_type: str,
):
    return (
        db.query(Alert)
        .filter(
            Alert.battery_id == battery_id,
            Alert.alert_type == alert_type,
            Alert.is_read.is_(False),
        )
        .first()
        is not None
    )
def create_alert(
    db: Session,
    battery: Battery,
    alert_type: str,
    severity: str,
    title: str,
    message: str,
):
    if alert_exists(db, battery.id, alert_type):
        return None

    alert = Alert(
        organization_id=battery.organization_id,
        battery_id=battery.id,
        alert_type=alert_type,
        severity=severity,
        title=title,
        message=message,
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert
def generate_alerts_from_inspection(
    db: Session,
    inspection: Inspection,
):
    battery = (
        db.query(Battery)
        .filter(Battery.id == inspection.battery_id)
        .first()
    )

    if battery is None:
        return

    # -------------------------
    # LOW HEALTH ALERT
    # -------------------------

    if inspection.health_score < 70:
        create_alert(
            db=db,
            battery=battery,
            alert_type="LOW_HEALTH",
            severity="Critical",
            title="Battery health is critically low",
            message=(
                f"Battery {battery.serial_number} health score "
                f"is {inspection.health_score}%."
            ),
        )

    elif inspection.health_score < 80:
        create_alert(
            db=db,
            battery=battery,
            alert_type="LOW_HEALTH",
            severity="Medium",
            title="Battery health requires attention",
            message=(
                f"Battery {battery.serial_number} health score "
                f"is {inspection.health_score}%."
            ),
        )

    # -------------------------
    # HIGH TEMPERATURE ALERT
    # -------------------------

    if inspection.temperature > 45:
        create_alert(
            db=db,
            battery=battery,
            alert_type="HIGH_TEMPERATURE",
            severity="High",
            title="Battery temperature is too high",
            message=(
                f"Battery {battery.serial_number} temperature reached "
                f"{inspection.temperature}°C."
            ),
        )
def generate_warranty_expiry_alerts(
    db: Session,
    current_user: User,
):
    today = date.today()
    expiry_limit = today + timedelta(days=30)

    batteries = (
        db.query(Battery)
        .filter(
            Battery.organization_id == current_user.organization_id,
            Battery.warranty_end_date.is_not(None),
            Battery.warranty_end_date >= today,
            Battery.warranty_end_date <= expiry_limit,
            Battery.lifecycle_status.notin_(["Retired", "Recycled"]),
        )
        .all()
    )

    created_count = 0

    for battery in batteries:
        days_remaining = (
            battery.warranty_end_date - today
        ).days

        alert = create_alert(
            db=db,
            battery=battery,
            alert_type="WARRANTY_EXPIRY",
            severity="Medium",
            title="Battery warranty expiring soon",
            message=(
                f"Battery {battery.serial_number} warranty expires "
                f"on {battery.warranty_end_date}. "
                f"{days_remaining} day(s) remaining."
            ),
        )

        if alert is not None:
            created_count += 1

    return created_count
def generate_overdue_maintenance_alerts(
    db: Session,
    current_user: User,
):
    today = date.today()

    maintenance_records = (
        db.query(Maintenance)
        .join(Battery)
        .filter(
            Battery.organization_id == current_user.organization_id,
            Maintenance.scheduled_date < today,
            Battery.lifecycle_status.notin_(["Retired", "Recycled"]),
        )
        .all()
    )

    created_count = 0

    for maintenance in maintenance_records:

        # Skip completed maintenance
        if maintenance.status == "Completed":
            continue

        battery = maintenance.battery

        alert = create_alert(
            db=db,
            battery=battery,
            alert_type="OVERDUE_MAINTENANCE",
            severity="High",
            title="Battery maintenance overdue",
            message=(
                f"Maintenance for battery {battery.serial_number} "
                f"was scheduled for {maintenance.scheduled_date} "
                f"and is overdue."
            ),
        )

        if alert is not None:
            created_count += 1

    return created_count
def run_alert_scan(
    db: Session,
    current_user: User,
):
    warranty_alerts = generate_warranty_expiry_alerts(
        db=db,
        current_user=current_user,
    )

    maintenance_alerts = generate_overdue_maintenance_alerts(
        db=db,
        current_user=current_user,
    )

    return {
        "warranty_alerts_created": warranty_alerts,
        "maintenance_alerts_created": maintenance_alerts,
        "total_alerts_created": (
            warranty_alerts + maintenance_alerts
        ),
    }