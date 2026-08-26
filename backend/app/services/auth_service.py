from backend.app.schemas import user
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest
from backend.app.utils.auth import create_access_token
from backend.app.utils.security import verify_password


def login_user(
    db: Session,
    email: str,
    password: str,
):
    user = db.query(User).filter(
        User.email == email
    ).first()

    if user is None:
        return None

    if not user.is_active:
        return None
    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    token = create_access_token(
        {
            "sub": user.email,
            "user_id": user.id,
            "organization_id": user.organization_id,
            "role": user.role,
        }
    )

    return token