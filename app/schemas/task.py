from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator
import uuid


class TaskPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TargetType(str, Enum):
    PRODUCT = "PRODUCT"
    CATEGORY = "CATEGORY"
    SUPPLIER = "SUPPLIER"
    NONE = "NONE"


def normalize_target(
    target_type: TargetType | None,
    target_id: uuid.UUID | None
) -> tuple[TargetType, uuid.UUID | None]:
    normalized_type = target_type or TargetType.NONE

    if normalized_type == TargetType.NONE:
        if target_id is not None:
            raise ValueError(
                "target_id must be null when target_type is NONE"
            )

        return normalized_type, None

    # target_type is set; target_id is optional (a type-level
    # task without a specific record is allowed so it can
    # authorize creating new records of that type).

    return normalized_type, target_id


class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=150)

    description: str | None = Field(
        default=None,
        max_length=500)

    priority: TaskPriority = TaskPriority.MEDIUM

    due_date: datetime | None = None

    assigned_to_id: uuid.UUID

    target_type: TargetType | None = None

    target_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def validate_target(self):
        _, _ = normalize_target(
            self.target_type,
            self.target_id
        )

        return self


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=150)

    description: str | None = Field(
        default=None,
        max_length=500)

    priority: TaskPriority | None = None

    status: TaskStatus | None = None

    due_date: datetime | None = None

    assigned_to_id: uuid.UUID | None = None

    target_type: TargetType | None = None

    target_id: uuid.UUID | None = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    due_date: datetime | None
    assigned_to_id: uuid.UUID
    assigned_by_id: uuid.UUID
    target_type: TargetType | None
    target_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True)


class TaskListResponse(BaseModel):
    items: list[TaskResponse]