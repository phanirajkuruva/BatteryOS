import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.app.models.attachment import Attachment
from backend.app.models.battery import Battery
from backend.app.models.inspection import Inspection
from backend.app.models.user import User

#Base URL for uploaded files
BASE_URL = "http://127.0.0.1:8000"
# Base upload folder
UPLOAD_FOLDER = Path("backend/uploads")

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}

# Maximum file size (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


def upload_attachment(
        
    db: Session,
    inspection_id: int,
    file: UploadFile,
    current_user: User,
):
    """
    Upload an attachment for an inspection.
    """

    # ---------------------------------------------------
    # Step 1 — Verify inspection belongs to user's organization
    # ---------------------------------------------------
    inspection = (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Inspection.id == inspection_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )

    if inspection is None:
        raise HTTPException(
            status_code=404,
            detail="Inspection not found in your organization.",
        )

    # ---------------------------------------------------
    # Step 2 — Validate extension
    # ---------------------------------------------------
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and PDF files are allowed.",
        )

    # ---------------------------------------------------
    # Step 3 — Read file once and validate size
    # ---------------------------------------------------
    file_bytes = file.file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10 MB.",
        )

    # Reset pointer after reading
    file.file.seek(0)

    # ---------------------------------------------------
    # Step 4 — Decide upload folder
    # ---------------------------------------------------
    if extension == ".pdf":
        destination_folder = UPLOAD_FOLDER / "reports"
    else:
        destination_folder = UPLOAD_FOLDER / "images"

    destination_folder.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------
    # Step 5 — Generate unique filename
    # ---------------------------------------------------
    unique_name = (
        f"inspection_{inspection_id}_{uuid.uuid4().hex[:8]}{extension}"
    )

    destination_path = destination_folder / unique_name

    # ---------------------------------------------------
    # Step 6 — Save file to disk
    # ---------------------------------------------------
    with open(destination_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ---------------------------------------------------
    # Step 7 — Save metadata into PostgreSQL
    # ---------------------------------------------------
    attachment = Attachment(
        inspection_id=inspection_id,
        uploaded_by=current_user.id,
        original_name=file.filename,
        stored_name=unique_name,
        file_path=str(destination_path).replace("\\", "/"),
        file_type=file.content_type,
    )

    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return attachment

def get_inspection_attachments(
    db: Session,
    inspection_id: int,
    current_user: User,
):
    inspection = (
        db.query(Inspection)
        .join(Battery)
        .filter(
            Inspection.id == inspection_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )

    if inspection is None:
        return None

    attachments = (
        db.query(Attachment)
        .filter(
            Attachment.inspection_id == inspection_id,
        )
        .order_by(Attachment.created_at.desc())
        .all()
    )

    results = []

    for attachment in attachments:
        relative_path = attachment.file_path.replace("backend/", "")

        results.append(
            {
                "id": attachment.id,
                "inspection_id": attachment.inspection_id,
                "original_name": attachment.original_name,
                "stored_name": attachment.stored_name,
                "file_type": attachment.file_type,
                "file_path": attachment.file_path,
                "file_url": f"{BASE_URL}/{relative_path}",
                "uploaded_by": attachment.uploaded_by,
                "created_at": attachment.created_at,
            }
        )

    return results

def delete_attachment(
    db: Session,
    attachment_id: int,
    current_user: User,
):
    attachment = (
        db.query(Attachment)
        .join(Inspection)
        .join(Battery)
        .filter(
            Attachment.id == attachment_id,
            Battery.organization_id == current_user.organization_id,
        )
        .first()
    )

    if attachment is None:
        return False

    if os.path.exists(attachment.file_path):
        os.remove(attachment.file_path)

    db.delete(attachment)
    db.commit()

    return True