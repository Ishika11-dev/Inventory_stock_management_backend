from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services import procurement_service
from app.utils.exceptions import BadRequestException, ConflictException, NotFoundException


def _translate(error):
    if isinstance(error, NotFoundException):
        code = status.HTTP_404_NOT_FOUND
    elif isinstance(error, ConflictException):
        code = status.HTTP_409_CONFLICT
    else:
        code = status.HTTP_400_BAD_REQUEST
    raise HTTPException(status_code=code, detail=error.message)


def create_purchase_order(db: Session, data):
    try:
        return procurement_service.create_purchase_order(db, data)
    except (BadRequestException, ConflictException, NotFoundException) as error:
        _translate(error)


def receive_purchase_order(db: Session, purchase_order_id, data, actor_id=None):
    try:
        return procurement_service.receive_purchase_order(db, purchase_order_id, data, actor_id)
    except (BadRequestException, ConflictException, NotFoundException) as error:
        _translate(error)
