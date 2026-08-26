from fastapi import APIRouter, Depends

from backend.app.models.user import User
from backend.app.utils.auth import get_current_user

router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


@router.get("/me")
def my_profile(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "name": current_user.full_name,
        "email": current_user.email,
        "organization_id": current_user.organization_id,
        "role": current_user.role,
    }