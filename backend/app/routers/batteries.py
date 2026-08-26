from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.schemas.battery import (
    BatteryCreate,
    BatteryResponse,
)
from backend.app.services.battery_service import (
    get_all_batteries,
    get_battery_by_id,
    create_battery,
    update_battery,
    delete_battery,
    get_batteries_by_organization,
)
from backend.app.models.user import User
from backend.app.utils.auth import get_current_user
from backend.app.utils.permissions import require_roles

router = APIRouter(
    prefix="/batteries",
    tags=["Batteries"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[BatteryResponse])
def get_batteries_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_all_batteries(db,current_user)


@router.get("/{battery_id}", response_model=BatteryResponse)
def get_battery_endpoint(
    battery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    battery = get_battery_by_id(db, battery_id,current_user)

    if battery is None:
        raise HTTPException(
            status_code=404,
            detail="Battery not found",
        )

    return battery


@router.post("/", response_model=BatteryResponse)
def create_battery_endpoint(
    battery: BatteryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Owner", "Admin","Technician",))
):
    return create_battery(db, battery,current_user,)


@router.put("/{battery_id}", response_model=BatteryResponse)
def update_battery_endpoint(
    battery_id: int,
    battery: BatteryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Owner", "Admin","Technician",))
):
    updated_battery = update_battery(
        db,
        battery_id,
        battery
    )

    if updated_battery is None:
        raise HTTPException(
            status_code=404,
            detail="Battery or Organization not found"
        )

    return updated_battery


@router.delete("/{battery_id}")
def delete_battery_endpoint(
    battery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("Owner", "Admin",))
):
    deleted = delete_battery(
        db,
        battery_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Battery not found"
        )

    return {
        "message": "Battery deleted successfully",
        "battery_id": battery_id
    }
@router.get(
    "/organization/{organization_id}",
    response_model=list[BatteryResponse]
)
def batteries_by_organization(
    organization_id: int,
    db: Session = Depends(get_db)
):
    return get_batteries_by_organization(db, organization_id)