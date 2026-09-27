from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

#from backend.app.database import get_db
from backend.app.database import SessionLocal
from backend.app.models.user import User
from backend.app.schemas.dashboard import (
    DashboardSummaryResponse,
    HealthTrendItem,
    RecentInspectionItem,
    CriticalBatteryItem,
    UpcomingMaintenanceItem,
    WarrantyExpiringItem,
    RecentAlertItem,
)
from backend.app.services.dashboard_service import( 
    get_dashboard_summary,
    get_health_trend,
    get_recent_inspections,
    get_critical_batteries,
    get_upcoming_maintenance,
    get_expiring_warranties,
    get_recent_alerts
)
from backend.app.utils.permissions import require_roles

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
)
def dashboard_summary(
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
    return get_dashboard_summary(
        db,
        current_user,
    )
@router.get(
    "/health-trend",
    response_model=list[HealthTrendItem],
)
def health_trend(
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
    return get_health_trend(db, current_user)
@router.get(
    "/recent-inspections",
    response_model=list[RecentInspectionItem],
)
def recent_inspections(
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
    return get_recent_inspections(db, current_user)

@router.get(
    "/critical-batteries",
    response_model=list[CriticalBatteryItem],
)
def critical_batteries(
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
    return get_critical_batteries(db, current_user)
@router.get("/upcoming-maintenance",response_model=list[UpcomingMaintenanceItem],)
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
@router.get("/warranty-expiring",response_model=list[WarrantyExpiringItem],)
def warranty_expiring(
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
    return get_expiring_warranties(
        db,
        current_user,
    )
@router.get("/recent-alerts",response_model=list[RecentAlertItem],)
def recent_alerts(
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
    return get_recent_alerts(
        db,
        current_user,
    )