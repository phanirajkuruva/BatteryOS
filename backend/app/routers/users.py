from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.schemas.user import (
    UserCreate,
    UserResponse,
    UserRoleUpdate,
    UserStatusUpdate,
)
from backend.app.services.user_service import create_user
from backend.app.models.user import User
from backend.app.utils.auth import get_current_user
from backend.app.services.user_service import get_my_profile
from backend.app.utils.permissions import require_roles
from backend.app.services.user_service import (
    get_users_by_organization,
    get_user_by_id,
    update_user_role,
    update_user_status,
    delete_user,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=list[UserResponse]
)
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Owner", "Admin")
    ),
):
    return get_users_by_organization(
        db,
        current_user,
    )
@router.get("/me", response_model=UserResponse)
def my_profile(
    current_user: User = Depends(get_current_user),
):
    return get_my_profile(current_user)
@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Owner", "Admin")
    ),
):
    user = get_user_by_id(
        db,
        user_id,
        current_user,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user
@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    new_user, error = create_user(db, user)

    if error == "organization_not_found":
        raise HTTPException(
            status_code=404,
            detail="Organization not found"
        )

    if error == "email_exists":
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    return new_user


@router.put(
    "/{user_id}/role",
    response_model=UserResponse
)
def update_role(
    user_id: int,
    request: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Owner")
    ),
):
    user = update_user_role(
        db,
        user_id,
        request.role.value,
        current_user,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user
@router.patch(
    "/{user_id}/status",
    response_model=UserResponse
)
def update_status(
    user_id: int,
    request: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Owner", "Admin")
    ),
):
    user = update_user_status(
        db,
        user_id,
        request.is_active,
        current_user,
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user
@router.delete("/{user_id}")
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles("Owner")
    ),
):
    deleted = delete_user(
        db,
        user_id,
        current_user,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return {
        "message": "User deleted successfully",
        "user_id": user_id,
    }