from sqlalchemy.orm import Session

from backend.app.models.organization import Organization
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate
from backend.app.utils.security import hash_password


def create_user(db: Session, user: UserCreate):
    # Check organization exists
    organization = db.query(Organization).filter(
        Organization.id == user.organization_id
    ).first()

    if organization is None:
        return None, "organization_not_found"

    # Check duplicate email
    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        return None, "email_exists"

    new_user = User(
        organization_id=user.organization_id,
        full_name=user.full_name,
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role.value,
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user, None

def get_my_profile(current_user: User):
    return current_user

def get_users_by_organization(
    db: Session,
    current_user: User,
):
    return (
        db.query(User)
        .filter(
            User.organization_id == current_user.organization_id
        )
        .order_by(User.created_at.desc())
        .all()
    )
def get_user_by_id(
    db: Session,
    user_id: int,
    current_user: User,
):
    return (
        db.query(User)
        .filter(
            User.id == user_id,
            User.organization_id == current_user.organization_id,
        )
        .first()
    )
def update_user_role(
    db: Session,
    user_id: int,
    role: str,
    current_user: User,
):
    user = get_user_by_id(
        db,
        user_id,
        current_user,
    )

    if user is None:
        return None

    user.role = role

    db.commit()
    db.refresh(user)

    return user
def update_user_status(
    db: Session,
    user_id: int,
    is_active: bool,
    current_user: User,
):
    user = get_user_by_id(
        db,
        user_id,
        current_user,
    )

    if user is None:
        return None

    user.is_active = is_active

    db.commit()
    db.refresh(user)

    return user
def delete_user(
    db: Session,
    user_id: int,
    current_user: User,
):
    user = get_user_by_id(
        db,
        user_id,
        current_user,
    )

    if user is None:
        return False

    db.delete(user)
    db.commit()

    return True