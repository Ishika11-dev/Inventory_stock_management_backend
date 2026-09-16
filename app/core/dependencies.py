from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.revoked_token import RevokedToken
from app.models.task import Task
from app.schemas.auth import UserRole

security = HTTPBearer()

SUPER_ADMIN = UserRole.SUPER_ADMIN.value
ADMIN_MANAGER = UserRole.ADMIN_MANAGER.value
STAFF_MANAGER = UserRole.STAFF_MANAGER.value
ADMIN = UserRole.ADMIN.value
STAFF = UserRole.STAFF.value

MANAGER_ROLES = {ADMIN_MANAGER, STAFF_MANAGER}
UNRESTRICTED_ROLES = {SUPER_ADMIN, ADMIN_MANAGER, STAFF_MANAGER}
WORKER_ROLES = {ADMIN, STAFF}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = decode_access_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    # Make sure this is an access token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    # Check whether token contains jti
    jti = payload.get("jti")

    if not jti:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    # Check whether token has been revoked
    revoked_token = (
        db.query(RevokedToken)
        .filter(RevokedToken.jti == jti)
        .first()
    )

    if revoked_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )

    # Get user ID from JWT
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = (
        db.query(User)
        .filter(User.id == uuid.UUID(user_id))
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


def require_super_admin(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )

    return current_user


def require_manager(
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in MANAGER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required"
        )

    return current_user


def require_super_admin_or_manager(
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in UNRESTRICTED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return current_user


# --------------------------------
# TASK-COVERAGE HELPERS
# --------------------------------


def has_unrestricted_access(user: User) -> bool:
    return user.role in UNRESTRICTED_ROLES


def is_worker(user: User) -> bool:
    return user.role in WORKER_ROLES


def _active_assigned_tasks(
    db: Session,
    user: User,
    target_type: str
):
    return (
        db.query(Task)
        .filter(
            Task.assigned_to_id == user.id,
            Task.status != "COMPLETED",
            Task.target_type == target_type,
        )
    )


def ensure_record_access(
    db: Session,
    user: User,
    target_type: str,
    target_id
):
    """Workers can only access a record referenced by an
    active assigned task. Managers and super admin pass."""

    if has_unrestricted_access(user):
        return

    task = _active_assigned_tasks(
        db, user, target_type
    ).filter(Task.target_id == target_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "No active task assigned to you "
                "references this record"
            )
        )


def ensure_create_access(
    db: Session,
    user: User,
    target_type: str
):
    """Workers can only create a new record when they have an
    active assigned task of the matching target type."""

    if has_unrestricted_access(user):
        return

    task = _active_assigned_tasks(
        db, user, target_type
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "No active task of the required type "
                "assigned to you"
            )
        )


def get_covered_target_ids(
    db: Session,
    user: User,
    target_type: str
):
    """Read access is unrestricted for all authenticated roles —
    every user can view all records in lists and summaries.
    Write access is separately enforced by ensure_record_access /
    ensure_create_access. Always returns None (no list filtering)."""

    return None