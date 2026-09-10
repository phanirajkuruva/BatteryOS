from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

#from backend.app.database import get_db
from backend.app.database import SessionLocal
from backend.app.models.user import User
from backend.app.services.certificate_service import (
    generate_certificate,
    verify_certificate
)
from backend.app.utils.permissions import require_roles

router = APIRouter(
    prefix="/certificates",
    tags=["Certificates"],
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/inspection/{inspection_id}")
def download_certificate(
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
    pdf_path = generate_certificate(
        db,
        inspection_id,
        current_user,
    )

    if pdf_path is None:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found in your organization.",
        )

    return FileResponse(
        path=pdf_path,
        filename=f"battery_certificate_{inspection_id}.pdf",
        media_type="application/pdf",
    )

@router.get("/verify/{inspection_id}")
def verify_certificate_endpoint(
    inspection_id: int,
    db: Session = Depends(get_db),
):
    result = verify_certificate(
        db,
        inspection_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found.",
        )

    return result