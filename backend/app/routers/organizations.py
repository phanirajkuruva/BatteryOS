from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.models.user import User
from backend.app.utils.auth import get_current_user
from backend.app.services.organization_service import (
    get_my_organization,
)

from backend.app.database import SessionLocal
from backend.app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse
)
from backend.app.services.organization_service import (
    get_all_organizations,
    get_organization_by_id,
    create_organization
)

router = APIRouter(
    prefix="/organizations",
    tags=["Organizations"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=list[OrganizationResponse])
def get_organizations(db: Session = Depends(get_db)):
    return get_all_organizations(db)

@router.get("/me", response_model=OrganizationResponse)
def my_organization(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    organization = get_my_organization(
        db,
        current_user,
    )

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found",
        )

    return organization

@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db)
):
    organization = get_organization_by_id(db, organization_id)

    if organization is None:
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    return organization


@router.post("/", response_model=OrganizationResponse)
def create_new_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db)
):
    new_org = create_organization(db, organization)

    if new_org is None:
        raise HTTPException(
            status_code=409,
            detail="Organization email already exists"
        )

    return new_org
