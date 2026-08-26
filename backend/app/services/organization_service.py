from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.app.models.organization import Organization
from backend.app.schemas.organization import OrganizationCreate
from backend.app.models.user import User


def get_all_organizations(db: Session):
    return db.query(Organization).all()


def get_organization_by_id(db: Session, organization_id: int):
    return db.query(Organization).filter(
        Organization.id == organization_id
    ).first()


def create_organization(db: Session, organization: OrganizationCreate):
    new_org = Organization(
        name=organization.name,
        email=organization.email,
        phone=organization.phone,
        address=organization.address,
        country=organization.country
    )

    try:
        db.add(new_org)
        db.commit()
        db.refresh(new_org)
    except IntegrityError:
        db.rollback()
        return None
    return new_org
def get_my_organization(
    db: Session,
    current_user: User,
):
    return (
        db.query(Organization)
        .filter(
            Organization.id == current_user.organization_id
        )
        .first()
    )