from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.schemas.battery import (
    BatteryCreate,
    BatteryResponse,
    BatteryWithInspectionsResponse,
    BatteryDashboardSummaryResponse,
    WarrantySummaryResponse,
    LifecycleSummaryResponse,
)
from backend.app.services.battery_service import (
    get_all_batteries,
    get_battery_by_id,
    create_battery,
    update_battery,
    delete_battery,
    get_batteries_by_organization,
    get_battery_with_history,
    get_battery_dashboard_summary,
    get_warranty_expiring_batteries,
    get_expired_warranty_batteries,
    get_warranty_summary,
    get_lifecycle_summary,
)
from backend.app.models.user import User
from backend.app.utils.auth import get_current_user
from backend.app.utils.permissions import require_roles
from backend.app.schemas.battery import BatteryLifecycleUpdate
from backend.app.services.battery_service import update_lifecycle_status

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

@router.get(
    "/{battery_id}/history",
    response_model=BatteryWithInspectionsResponse,
)
def battery_history(
    battery_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Technician",
            "Viewer",
        )
    ),
):
    battery = get_battery_with_history(
        db,
        battery_id,
        current_user,
    )

    if battery is None:
        raise HTTPException(
            status_code=404,
            detail="Battery not found in your organization.",
        )

    return battery

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

@router.put(
    "/{battery_id}/lifecycle",
    response_model=BatteryResponse,
)
def update_battery_lifecycle(
    battery_id: int,
    lifecycle: BatteryLifecycleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
        )
    ),
):
    updated_battery = update_lifecycle_status(
        db=db,
        battery_id=battery_id,
        lifecycle_status=lifecycle.lifecycle_status.value,
        retired_date=lifecycle.retired_date,
        retirement_reason=lifecycle.retirement_reason,
        current_user=current_user,
    )

    if updated_battery is None:
        raise HTTPException(
            status_code=404,
            detail="Battery not found in your organization.",
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
@router.get("/organization/{organization_id}",response_model=list[BatteryResponse])
def batteries_by_organization(
    organization_id: int,
    db: Session = Depends(get_db)
):
    return get_batteries_by_organization(db, organization_id)
@router.get("/dashboard/summary",response_model=BatteryDashboardSummaryResponse,)
def battery_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Technician",
            "Viewer",
        )
    ),
):
    return get_battery_dashboard_summary(
        db,
        current_user,
    )
@router.get("/dashboard/warranty-expiring",response_model=list[BatteryResponse],)
def warranty_expiring_batteries(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Technician",
            "Viewer",
        )
    ),
):
    return get_warranty_expiring_batteries(
        db,
        current_user,
    )
@router.get("/dashboard/warranty-expired",response_model=list[BatteryResponse],)
def warranty_expired_batteries(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Technician",
            "Viewer",
        )
    ),
):
    return get_expired_warranty_batteries(
        db,
        current_user,
    )
@router.get("/dashboard/warranty-summary",response_model=WarrantySummaryResponse,)
def warranty_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Viewer",
        )
    ),
):
    return get_warranty_summary(
        db,
        current_user,
    )
@router.get("/dashboard/lifecycle-summary",response_model=LifecycleSummaryResponse,)
def lifecycle_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Viewer",
        )
    ),
):
    return get_lifecycle_summary(
        db,
        current_user,
    )