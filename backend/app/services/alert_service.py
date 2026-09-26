from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.alert import Alert
from backend.app.models.user import User


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