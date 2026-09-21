from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services import order_service
from app.utils.exceptions import BadRequestException, NotFoundException


def _translate(error):
    if isinstance(error, NotFoundException):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error.message)


def create_customer(db: Session, data):
    try:
        return order_service.create_customer(db, data)
    except (BadRequestException, NotFoundException) as error:
        _translate(error)


def create_order(db: Session, data, actor_id=None):
    try:
        return order_service.create_order(db, data, actor_id)
    except (BadRequestException, NotFoundException) as error:
        _translate(error)


def update_status(db: Session, order_id, data, actor_id=None):
    try:
        return order_service.update_status(db, order_id, data.status.value, actor_id, data.note)
    except (BadRequestException, NotFoundException) as error:
        _translate(error)
