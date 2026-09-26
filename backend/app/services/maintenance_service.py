from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from backend.app.models.maintenance import Maintenance
from backend.app.models.battery import Battery
from backend.app.models.user import User
from backend.app.schemas.maintenance import (
    MaintenanceCreate,
    MaintenanceUpdate,
)
from datetime import date, timedelta
VALID_STATUSES = {
    "Scheduled",
    "In Progress",
    "Completed",
}

VALID_TRANSITIONS = {
    "Scheduled": ["In Progress"],
    "In Progress": ["Completed"],
    "Completed": [],
}

def create_maintenance(
    db: Session,
    maintenance: MaintenanceCreate,
    current_user: User,
):
    # Verify battery belongs to user's organization
    battery = (
        db.query(Battery)
        .filter(
            Battery.id == maintenance.battery_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )

    if battery is None:
        return None

    new_record = Maintenance(
        battery_id=maintenance.battery_id,
        assigned_to=maintenance.assigned_to,
        maintenance_type=maintenance.maintenance_type,
        scheduled_date=maintenance.scheduled_date,
        cost=maintenance.cost,
        notes=maintenance.notes,
        status="Scheduled",
    )

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record

def get_maintenance_records(
    db: Session,
    current_user: User,
):
    return (
        db.query(Maintenance)
        .join(Battery)
        .filter(
            Battery.organization_id == current_user.organization_id,
        )
        .order_by(Maintenance.scheduled_date.desc())
        .all()
    )
def get_maintenance_by_id(
    db: Session,
    maintenance_id: int,
    current_user: User,
):
    return (
        db.query(Maintenance)
        .join(Battery)
        .filter(
            Maintenance.id == maintenance_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )
def update_maintenance(
    db: Session,
    maintenance_id: int,
    maintenance_update: MaintenanceUpdate,
    current_user: User,
):
    record = get_maintenance_by_id(
        db,
        maintenance_id,
        current_user,
    )

    if record is None:
        return None

    update_data = maintenance_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)

    return record
def delete_maintenance(
    db: Session,
    maintenance_id: int,
    current_user: User,
):
    record = get_maintenance_by_id(
        db,
        maintenance_id,
        current_user,
    )

    if record is None:
        return False

    db.delete(record)
    db.commit()

    return True
def assign_technician(
    db: Session,
    maintenance_id: int,
    technician_id: int,
    current_user: User,
):
    record = get_maintenance_by_id(
        db,
        maintenance_id,
        current_user,
    )

    if record is None:
        return None

    technician = (
        db.query(User)
        .filter(
            User.id == technician_id,
            User.organization_id == current_user.organization_id,
            User.role == "Technician",
            User.is_active == True,
        )
        .first()
    )

    if technician is None:
        raise HTTPException(
            status_code=404,
            detail="Technician not found in your organization.",
        )

    record.assigned_to = technician.id

    db.commit()
    db.refresh(record)

    return record

def update_maintenance_status(
    db: Session,
    maintenance_id: int,
    new_status: str,
    completed_date,
    current_user: User,
):
    record = get_maintenance_by_id(
        db,
        maintenance_id,
        current_user,
    )

    if record is None:
        return None

    if new_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="Invalid maintenance status.",
        )

    current_status = record.status

    if new_status == current_status:
        raise HTTPException(
            status_code=400,
            detail="Maintenance is already in this status.",
        )

    allowed = VALID_TRANSITIONS[current_status]

    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change status from '{current_status}' to '{new_status}'.",
        )

    if new_status == "Completed":
        if completed_date is None:
            raise HTTPException(
                status_code=400,
                detail="completed_date is required when maintenance is completed.",
            )

        record.completed_date = completed_date

    record.status = new_status

    db.commit()
    db.refresh(record)

    return record

def get_maintenance_summary(
    db: Session,
    current_user: User,
):
    maintenance = (
        db.query(Maintenance)
        .join(Battery)
        .filter(
            Battery.organization_id == current_user.organization_id,
        )
    )

    return {
        "total_jobs": maintenance.count(),
        "scheduled": maintenance.filter(
            Maintenance.status == "Scheduled"
        ).count(),
        "in_progress": maintenance.filter(
            Maintenance.status == "In Progress"
        ).count(),
        "completed": maintenance.filter(
            Maintenance.status == "Completed"
        ).count(),
    }
def get_upcoming_maintenance(
    db: Session,
    current_user: User,
):
    today = date.today()
    next_week = today + timedelta(days=7)

    return (
        db.query(Maintenance)
        .join(Battery)
        .filter(
            Battery.organization_id == current_user.organization_id,
            Maintenance.status != "Completed",
            Maintenance.scheduled_date >= today,
            Maintenance.scheduled_date <= next_week,
        )
        .order_by(Maintenance.scheduled_date)
        .all()
    )
def get_overdue_maintenance(
    db: Session,
    current_user: User,
):
    today = date.today()

    return (
        db.query(Maintenance)
        .join(Battery)
        .filter(
            Battery.organization_id == current_user.organization_id,
            Maintenance.status != "Completed",
            Maintenance.scheduled_date < today,
        )
        .order_by(Maintenance.scheduled_date)
        .all()
    )
def get_cost_summary(
    db: Session,
    current_user: User,
):
    result = (
        db.query(
            func.sum(Maintenance.cost),
            func.count(Maintenance.id),
        )
        .join(Battery)
        .filter(
            Battery.organization_id == current_user.organization_id,
            Maintenance.status == "Completed",
        )
        .first()
    )

    total_cost = result[0] if result[0] else 0
    completed_jobs = result[1]

    return {
        "total_cost": total_cost,
        "total_completed_jobs": completed_jobs,
    }
def get_cost_by_battery(
    db: Session,
    current_user: User,
):
    results = (
        db.query(
            Battery.id,
            Battery.serial_number,
            func.sum(Maintenance.cost).label("total_cost"),
        )
        .join(Maintenance)
        .filter(
            Battery.organization_id == current_user.organization_id,
            Maintenance.status == "Completed",
        )
        .group_by(
            Battery.id,
            Battery.serial_number,
        )
        .all()
    )

    return [
        {
            "battery_id": row.id,
            "serial_number": row.serial_number,
            "total_cost": row.total_cost or 0,
        }
        for row in results
    ]