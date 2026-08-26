from fastapi import Depends, HTTPException, status

from backend.app.models.user import User
from backend.app.utils.auth import get_current_user


def require_roles(*allowed_roles):
    """
    Dependency that allows only specific user roles.
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
    ):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )

        return current_user

    return role_checker