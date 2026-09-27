from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.maintenance import (
    BatteryCostResponse,
    CostSummaryResponse,
    MaintenanceCreate,
    MaintenanceStatusUpdate,
    MaintenanceSummaryResponse,
    MaintenanceUpdate,
    MaintenanceResponse,
)
from backend.app.services.maintenance_service import (
    assign_technician,
    create_maintenance,
    get_maintenance_records,
    get_maintenance_by_id,
    update_maintenance,
    delete_maintenance,
    update_maintenance_status,
    get_maintenance_summary,
    get_upcoming_maintenance,
    get_overdue_maintenance,
    get_cost_summary,
    get_cost_by_battery,
)
from backend.app.utils.permissions import require_roles

router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"],
)

@router.post(
    "/",
    response_model=MaintenanceResponse,
)
def create_new_maintenance(
    maintenance: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
        )
    ),
):
    new_record = create_maintenance(
        db,
        maintenance,
        current_user,
    )

    if new_record is None:
        raise HTTPException(
            status_code=404,
            detail="Battery not found in your organization.",
        )

    return new_record

@router.get(
    "/",
    response_model=list[MaintenanceResponse],
)
def list_maintenance(
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
    return get_maintenance_records(
        db,
        current_user,
    )
@router.get(
    "/{maintenance_id}",
    response_model=MaintenanceResponse,
)
def get_single_maintenance(
    maintenance_id: int,
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
    record = get_maintenance_by_id(
        db,
        maintenance_id,
        current_user,
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found.",
        )

    return record
@router.put(
    "/{maintenance_id}",
    response_model=MaintenanceResponse,
)
def update_existing_maintenance(
    maintenance_id: int,
    maintenance: MaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Technician",
        )
    ),
):
    updated = update_maintenance(
        db,
        maintenance_id,
        maintenance,
        current_user,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found.",
        )

    return updated
@router.delete("/{maintenance_id}")
def remove_maintenance(
    maintenance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
        )
    ),
):
    deleted = delete_maintenance(
        db,
        maintenance_id,
        current_user,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found.",
        )

    return {
        "message": "Maintenance deleted successfully.",
        "maintenance_id": maintenance_id,
    }
@router.put(
    "/{maintenance_id}/assign/{technician_id}",
    response_model=MaintenanceResponse,
)
def assign_maintenance_technician(
    maintenance_id: int,
    technician_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
        )
    ),
):
    updated = assign_technician(
        db,
        maintenance_id,
        technician_id,
        current_user,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found.",
        )

    return updated
@router.put(
    "/{maintenance_id}/status",
    response_model=MaintenanceResponse,
)
def change_maintenance_status(
    maintenance_id: int,
    status_update: MaintenanceStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Technician",
        )
    ),
):
    updated = update_maintenance_status(
        db=db,
        maintenance_id=maintenance_id,
        new_status=status_update.status,
        completed_date=status_update.completed_date,
        current_user=current_user,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Maintenance record not found.",
        )

    return updated
@router.get(
    "/dashboard/summary",
    response_model=MaintenanceSummaryResponse,
)
def maintenance_summary(
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
    return get_maintenance_summary(
        db,
        current_user,
    )
@router.get(
    "/dashboard/upcoming",
    response_model=list[MaintenanceResponse],
)
def upcoming_maintenance(
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
    return get_upcoming_maintenance(
        db,
        current_user,
    )
@router.get(
    "/dashboard/overdue",
    response_model=list[MaintenanceResponse],
)
def overdue_maintenance(
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
    return get_overdue_maintenance(
        db,
        current_user,
    )
@router.get(
    "/dashboard/cost-summary",
    response_model=CostSummaryResponse,
)
def maintenance_cost_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Viewer",
        )
    ),
):
    return get_cost_summary(
        db,
        current_user,
    )
@router.get(
    "/dashboard/cost-by-battery",
    response_model=list[BatteryCostResponse],
)
def maintenance_cost_per_battery(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Viewer",
        )
    ),
):
    return get_cost_by_battery(
        db,
        current_user,
    )