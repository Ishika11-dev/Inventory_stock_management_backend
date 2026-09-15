from pydantic import BaseModel

from app.schemas.auth import UserRole


class RoleUpdateRequest(BaseModel):
    role: UserRole