from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.schemas.certificate import (
    CertificateCreate,
    CertificateResponse,
    CertificateVerificationResponse
)
from backend.app.services.certificate_service import (
    create_certificate,
    get_certificate_by_id,
    get_battery_certificates,
    revoke_certificate,
    generate_certificate_pdf,
    verify_certificate
)
from backend.app.utils.permissions import require_roles

router = APIRouter(
    prefix="/certificates",
    tags=["Certificates"],
)

# @router.get("/inspection/{inspection_id}")
# def download_certificate(
#     inspection_id: int,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(
#         require_roles(
#             "Owner",
#             "Admin",
#             "Technician",
#             "Viewer",
#         )
#     ),
# ):
#     pdf_path = generate_certificate(
#         db,
#         inspection_id,
#         current_user,
#     )

#     if pdf_path is None:
#         raise HTTPException(
#             status_code=404,
#             detail="Inspection not found in your organization.",
#         )

#     return FileResponse(
#         path=pdf_path,
#         filename=f"battery_certificate_{inspection_id}.pdf",
#         media_type="application/pdf",
#     )

@router.post("/",response_model=CertificateResponse,status_code=status.HTTP_201_CREATED,)
def create_certificate_endpoint(
    certificate: CertificateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
        )
    ),
):
    created_certificate = create_certificate(
        db=db,
        inspection_id=certificate.inspection_id,
        current_user=current_user,
    )

    if created_certificate is None:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found in your organization.",
        )

    return created_certificate
@router.get("/verify/{certificate_number}",response_model=CertificateVerificationResponse,)
def verify_certificate_endpoint(
    certificate_number: str,
    db: Session = Depends(get_db),
):
    result = verify_certificate(
        db=db,
        certificate_number=certificate_number,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found.",
        )

    return result
@router.get("/battery/{battery_id}",response_model=list[CertificateResponse],)
def get_battery_certificates_endpoint(
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
    certificates = get_battery_certificates(
        db=db,
        battery_id=battery_id,
        current_user=current_user,
    )

    if certificates is None:
        raise HTTPException(
            status_code=404,
            detail="Battery not found in your organization.",
        )

    return certificates
@router.get("/{certificate_id}/pdf",)
def download_certificate_pdf(
    certificate_id: int,
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
    pdf_path = generate_certificate_pdf(
        db=db,
        certificate_id=certificate_id,
        current_user=current_user,
    )

    if pdf_path is None:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found in your organization.",
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=f"battery_certificate_{certificate_id}.pdf",
    )
@router.get("/{certificate_id}",response_model=CertificateResponse,)
def get_certificate_endpoint(
    certificate_id: int,
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
    certificate = get_certificate_by_id(
        db=db,
        certificate_id=certificate_id,
        current_user=current_user,
    )

    if certificate is None:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found in your organization.",
        )

    return certificate
@router.put("/{certificate_id}/revoke",response_model=CertificateResponse,)
def revoke_certificate_endpoint(
    certificate_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
        )
    ),
):
    certificate = revoke_certificate(
        db=db,
        certificate_id=certificate_id,
        current_user=current_user,
    )

    if certificate is None:
        raise HTTPException(
            status_code=404,
            detail="Certificate not found in your organization.",
        )

    return certificate


