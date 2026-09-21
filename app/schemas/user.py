import uuid

from pydantic import BaseModel

from app.schemas.auth import UserRole


class RoleUpdateRequest(BaseModel):
    role: UserRole
    manager_id: uuid.UUID | None = None