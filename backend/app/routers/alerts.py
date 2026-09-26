from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.schemas.alert import (
    AlertResponse,
    AlertDashboardSummaryResponse,
)
from backend.app.services.alert_service import (
    get_all_alerts,
    get_unread_alerts,
    mark_alert_as_read,
    get_alert_dashboard_summary,
)
from backend.app.utils.permissions import require_roles
from backend.app.models.user import User

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@router.get("/",response_model=list[AlertResponse],)
def get_alerts(
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
    return get_all_alerts(
        db,
        current_user,
    )


@router.get("/unread",response_model=list[AlertResponse],)
def unread_alerts(
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
    return get_unread_alerts(
        db,
        current_user,
    )


@router.put("/{alert_id}/read", response_model=AlertResponse,)
def read_alert(
    alert_id: int,
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
    alert = mark_alert_as_read(
        db,
        alert_id,
        current_user,
    )

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found.",
        )

    return alert


@router.get("/dashboard/summary", response_model=AlertDashboardSummaryResponse,)
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Viewer",
        )
    ),
):
    return get_alert_dashboard_summary(
        db,
        current_user,
    )