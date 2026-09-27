from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.inspection import (
    InspectionCreate,
    InspectionResponse,
    InspectionUpdate,
)
from backend.app.services.inspection_service import (
    create_inspection,
    get_all_inspections,
    get_inspection_by_id,
    get_battery_inspections,
    update_inspection,
    delete_inspection,
)
from backend.app.utils.permissions import require_roles

router = APIRouter(
    prefix="/inspections",
    tags=["Inspections"],
)


@router.post(
    "/",
    response_model=InspectionResponse,
)
def create_new_inspection(
    inspection: InspectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Owner", "Admin", "Technician")
    ),
):
    new_inspection = create_inspection(
        db,
        inspection,
        current_user,
    )

    if new_inspection is None:
        raise HTTPException(
            status_code=404,
            detail="Battery not found in your organization.",
        )

    return new_inspection

@router.get(
    "/",
    response_model=list[InspectionResponse],
)
def get_inspections(
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
    return get_all_inspections(
        db,
        current_user,
    )

@router.get(
    "/{inspection_id}",
    response_model=InspectionResponse,
)
def get_inspection(
    inspection_id: int,
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
    inspection = get_inspection_by_id(
        db,
        inspection_id,
        current_user,
    )

    if inspection is None:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found.",
        )

    return inspection

@router.get(
    "/battery/{battery_id}",
    response_model=list[InspectionResponse],
)
def get_inspection_history(
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
    return get_battery_inspections(
        db,
        battery_id,
        current_user,
    )

@router.put(
    "/{inspection_id}",
    response_model=InspectionResponse,
)
def update_existing_inspection(
    inspection_id: int,
    inspection: InspectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Technician",
        )
    ),
):
    updated = update_inspection(
        db,
        inspection_id,
        inspection,
        current_user,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found in your organization.",
        )

    return updated

@router.delete(
    "/{inspection_id}",
)
def delete_existing_inspection(
    inspection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
        )
    ),
):
    deleted = delete_inspection(
        db,
        inspection_id,
        current_user,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found in your organization.",
        )

    return {
        "message": "Inspection deleted successfully.",
        "inspection_id": inspection_id,
    }