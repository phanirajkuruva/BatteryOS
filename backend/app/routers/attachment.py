import os

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
)
from sqlalchemy.orm import Session

from backend.app.database import SessionLocal
from backend.app.models.attachment import Attachment
from backend.app.models.inspection import Inspection
from backend.app.models.battery import Battery
from backend.app.models.user import User
from backend.app.schemas.attachment import AttachmentResponse
from backend.app.services.attachment_service import (
    upload_attachment,
    get_inspection_attachments,
    delete_attachment,
)
from backend.app.utils.permissions import require_roles

router = APIRouter(
    prefix="/attachments",
    tags=["Attachments"],
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
# ----------------------------------------------------
# Upload attachment to an inspection
# ----------------------------------------------------
@router.post(
    "/upload/{inspection_id}",
    response_model=AttachmentResponse,
)
def upload_inspection_attachment(
    inspection_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
            "Technician",
        )
    ),
):
    attachment = upload_attachment(
        db=db,
        inspection_id=inspection_id,
        file=file,
        current_user=current_user,
    )

    return attachment


# ----------------------------------------------------
# List all attachments of an inspection
# ----------------------------------------------------
@router.get(
    "/inspection/{inspection_id}",
    response_model=list[AttachmentResponse],
)
def list_attachments(
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
    attachments = get_inspection_attachments(
        db,
        inspection_id,
        current_user,
    )

    if attachments is None:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found in your organization.",
        )

    return attachments


# ----------------------------------------------------
# Delete attachment
# ----------------------------------------------------
@router.delete("/{attachment_id}")
def remove_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            "Owner",
            "Admin",
        )
    ),
):
    deleted = delete_attachment(
        db,
        attachment_id,
        current_user,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Attachment not found in your organization.",
        )

    return {
        "message": "Attachment deleted successfully.",
        "attachment_id": attachment_id,
    }