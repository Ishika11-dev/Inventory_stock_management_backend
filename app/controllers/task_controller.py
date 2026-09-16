from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.task import (
    TaskCreate,
    TaskStatusUpdate,
    TaskUpdate,
)

from app.services import task_service

from app.utils.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)


def create_task(
    db: Session,
    current_user: User,
    data: TaskCreate
):
    try:
        return task_service.create_task(
            db=db,
            current_user=current_user,
            data=data
        )

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )

    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )

    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


def list_tasks(
    db: Session,
    current_user: User
):
    try:
        return task_service.list_tasks(
            db=db,
            current_user=current_user
        )

    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )


def my_tasks(
    db: Session,
    current_user: User
):
    return task_service.my_tasks(
        db=db,
        current_user=current_user
    )


def get_task(
    db: Session,
    current_user: User,
    task_id
):
    try:
        return task_service.get_task(
            db=db,
            current_user=current_user,
            task_id=task_id
        )

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )

    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )


def update_task_status(
    db: Session,
    current_user: User,
    task_id,
    data: TaskStatusUpdate
):
    try:
        return task_service.update_task_status(
            db=db,
            current_user=current_user,
            task_id=task_id,
            status=data.status.value
        )

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )

    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )


def update_task(
    db: Session,
    current_user: User,
    task_id,
    data: TaskUpdate
):
    try:
        return task_service.update_task(
            db=db,
            current_user=current_user,
            task_id=task_id,
            data=data
        )

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )

    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )

    except BadRequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )


def delete_task(
    db: Session,
    current_user: User,
    task_id
):
    try:
        task_service.delete_task(
            db=db,
            current_user=current_user,
            task_id=task_id
        )

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )

    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )