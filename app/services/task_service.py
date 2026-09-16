from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.supplier import Supplier
from app.schemas.auth import UserRole
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TargetType,
)
from app.utils.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)

MANAGER_ROLES = {
    UserRole.ADMIN_MANAGER.value,
    UserRole.STAFF_MANAGER.value,
}

SUPER_ADMIN_ONLY_ROLE_CREATORS = {
    UserRole.SUPER_ADMIN.value,
    *MANAGER_ROLES,
}

TEAM_MAP = {
    UserRole.ADMIN_MANAGER.value: "ADMIN",
    UserRole.STAFF_MANAGER.value: "STAFF",
}

TARGET_MODEL = {
    TargetType.PRODUCT.value: Product,
    TargetType.CATEGORY.value: Category,
    TargetType.SUPPLIER.value: Supplier,
}


def _normalize_target(
    target_type,
    target_id
):
    if isinstance(target_type, TargetType):
        target_type = target_type.value

    normalized_type = (
        target_type or TargetType.NONE.value
    )

    if normalized_type == TargetType.NONE.value:
        if target_id is not None:
            raise BadRequestException(
                "target_id must be null "
                "when target_type is NONE"
            )

        return normalized_type, None

    # target_type is set; target_id is optional (a type-level
    # task without a specific record is allowed so it can
    # authorize creating new records of that type).

    return normalized_type, target_id


def _get_task(
    db: Session,
    task_id
):
    task = db.get(Task, task_id)

    if not task:
        raise NotFoundException(
            "Task not found"
        )

    return task


def _can_view(
    user: User,
    task: Task
) -> bool:
    if user.role == UserRole.SUPER_ADMIN.value:
        return True

    if user.role in MANAGER_ROLES:
        if task.assigned_by_id == user.id:
            return True

    if task.assigned_to_id == user.id:
        return True

    return False


def _can_manage(
    user: User,
    task: Task
) -> bool:
    if user.role == UserRole.SUPER_ADMIN.value:
        return True

    if user.role in MANAGER_ROLES:
        if task.assigned_by_id == user.id:
            return True

    return False


def _validate_assignee(
    db: Session,
    assigner: User,
    assignee_id
):
    assignee = db.get(User, assignee_id)

    if not assignee:
        raise NotFoundException(
            "Assigned user not found"
        )

    allowed_role = TEAM_MAP.get(assigner.role)

    if allowed_role is not None:
        if assignee.role != allowed_role:
            raise ForbiddenException(
                f"{assigner.role} can only "
                f"assign tasks to "
                f"{allowed_role} users"
            )

    return assignee


def _validate_target_exists(
    db: Session,
    normalized_type,
    normalized_id
):
    if normalized_type == TargetType.NONE.value:
        return

    model = TARGET_MODEL[normalized_type]

    if normalized_id and not db.get(model, normalized_id):
        raise NotFoundException(
            f"{normalized_type} not found"
        )


def create_task(
    db: Session,
    current_user: User,
    data: TaskCreate
):
    if current_user.role not in SUPER_ADMIN_ONLY_ROLE_CREATORS:
        raise ForbiddenException(
            "Only managers or the super admin "
            "can create tasks"
        )

    assignee = _validate_assignee(
        db,
        current_user,
        data.assigned_to_id
    )

    normalized_type, normalized_id = (
        _normalize_target(
            data.target_type,
            data.target_id
        )
    )

    _validate_target_exists(
        db,
        normalized_type,
        normalized_id
    )

    task = Task(
        title=data.title,
        description=data.description,
        priority=data.priority.value,
        status="PENDING",
        due_date=data.due_date,
        assigned_to_id=assignee.id,
        assigned_by_id=current_user.id,
        target_type=normalized_type,
        target_id=normalized_id,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def list_tasks(
    db: Session,
    current_user: User
):
    if current_user.role == UserRole.SUPER_ADMIN.value:
        return (
            db.query(Task)
            .order_by(Task.created_at.desc())
            .all()
        )

    if current_user.role in MANAGER_ROLES:
        return (
            db.query(Task)
            .filter(
                Task.assigned_by_id
                == current_user.id
            )
            .order_by(Task.created_at.desc())
            .all()
        )

    raise ForbiddenException(
        "Access denied"
    )


def my_tasks(
    db: Session,
    current_user: User
):
    return (
        db.query(Task)
        .filter(
            Task.assigned_to_id
            == current_user.id
        )
        .order_by(Task.created_at.desc())
        .all()
    )


def get_task(
    db: Session,
    current_user: User,
    task_id
):
    task = _get_task(db, task_id)

    if not _can_view(current_user, task):
        raise ForbiddenException(
            "Access denied"
        )

    return task


def update_task_status(
    db: Session,
    current_user: User,
    task_id,
    status
):
    task = _get_task(db, task_id)

    if not _can_view(current_user, task):
        raise ForbiddenException(
            "Access denied"
        )

    task.status = status

    db.commit()
    db.refresh(task)

    return task


def update_task(
    db: Session,
    current_user: User,
    task_id,
    data: TaskUpdate
):
    task = _get_task(db, task_id)

    if not _can_manage(current_user, task):
        raise ForbiddenException(
            "Access denied"
        )

    update_data = data.model_dump(
        exclude_unset=True
    )

    if "assigned_to_id" in update_data:
        assignee = _validate_assignee(
            db,
            current_user,
            update_data["assigned_to_id"]
        )

        update_data["assigned_to_id"] = assignee.id

    if (
        "target_type" in update_data
        or "target_id" in update_data
    ):
        new_target_type = update_data.get(
            "target_type",
            task.target_type
        )

        new_target_id = update_data.get(
            "target_id",
            task.target_id
        )

        normalized_type, normalized_id = (
            _normalize_target(
                new_target_type,
                new_target_id
            )
        )

        _validate_target_exists(
            db,
            normalized_type,
            normalized_id
        )

        update_data["target_type"] = normalized_type
        update_data["target_id"] = normalized_id

    for field, value in update_data.items():
        if field in ("priority", "status"):
            value = value.value

        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    return task


def delete_task(
    db: Session,
    current_user: User,
    task_id
):
    task = _get_task(db, task_id)

    if not _can_manage(current_user, task):
        raise ForbiddenException(
            "Access denied"
        )

    db.delete(task)
    db.commit()