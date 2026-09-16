from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.core.dependencies import (
    get_current_user,
    require_super_admin_or_manager,
)
from app.models.user import User

from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)

from app.controllers import task_controller

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_super_admin_or_manager
    ),
):
    return task_controller.create_task(
        db=db,
        current_user=current_user,
        data=data
    )


@router.get(
    "/",
    response_model=TaskListResponse
)
def get_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_super_admin_or_manager
    ),
):
    tasks = task_controller.list_tasks(
        db=db,
        current_user=current_user
    )

    return {"items": tasks}


@router.get(
    "/my",
    response_model=TaskListResponse
)
def get_my_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = task_controller.my_tasks(
        db=db,
        current_user=current_user
    )

    return {"items": tasks}


@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_controller.get_task(
        db=db,
        current_user=current_user,
        task_id=task_id
    )


@router.patch(
    "/{task_id}/status",
    response_model=TaskResponse
)
def update_task_status(
    task_id: uuid.UUID,
    data: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_controller.update_task_status(
        db=db,
        current_user=current_user,
        task_id=task_id,
        data=data
    )


@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_super_admin_or_manager
    ),
):
    return task_controller.update_task(
        db=db,
        current_user=current_user,
        task_id=task_id,
        data=data
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_task(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_super_admin_or_manager
    ),
):
    task_controller.delete_task(
        db=db,
        current_user=current_user,
        task_id=task_id
    )