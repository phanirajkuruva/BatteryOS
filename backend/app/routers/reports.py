from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.report import BatteryHealthReportResponse
from backend.app.services.report_service import (
    generate_battery_health_report,
    generate_battery_health_report_pdf,
)
from backend.app.utils.permissions import require_roles


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)

@router.get("/batteries/{battery_id}/health",response_model=BatteryHealthReportResponse,)
def get_battery_health_report(
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
    report = generate_battery_health_report(
        db=db,
        battery_id=battery_id,
        current_user=current_user,
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Battery not found in your organization.",
        )

    return report
@router.get("/batteries/{battery_id}/health/pdf",)
def download_battery_health_report(
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
    pdf_path = generate_battery_health_report_pdf(
        db=db,
        battery_id=battery_id,
        current_user=current_user,
    )

    if pdf_path is None:
        raise HTTPException(
            status_code=404,
            detail="Battery not found in your organization.",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"battery_health_report_{battery_id}.pdf",
    )