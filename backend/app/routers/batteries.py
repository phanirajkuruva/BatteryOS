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
)


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
def get_batteries(db: Session = Depends(get_db)):
    return get_all_batteries(db)


@router.get("/{battery_id}", response_model=BatteryResponse)
def get_battery(
    battery_id: int,
    db: Session = Depends(get_db)
):
    battery = get_battery_by_id(db, battery_id)

    if battery is None:
        raise HTTPException(
            status_code=404,
            detail="Battery not found"
        )

    return battery


@router.post("/", response_model=BatteryResponse)
def create_battery_endpoint(
    battery: BatteryCreate,
    db: Session = Depends(get_db)
):
    return create_battery(db, battery)


@router.put("/{battery_id}", response_model=BatteryResponse)
def update_battery_endpoint(
    battery_id: int,
    battery: BatteryCreate,
    db: Session = Depends(get_db)
):
    updated_battery = update_battery(
        db,
        battery_id,
        battery
    )

    if updated_battery is None:
        raise HTTPException(
            status_code=404,
            detail="Battery not found"
        )

    return updated_battery


@router.delete("/{battery_id}")
def delete_battery_endpoint(
    battery_id: int,
    db: Session = Depends(get_db)
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