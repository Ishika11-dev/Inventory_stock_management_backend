from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.services import prediction_service
from app.utils.exceptions import NotFoundException


def predict_order_delivery(db: Session, order_id):
    try:
        return prediction_service.predict_order_delivery(db, order_id)
    except NotFoundException as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error))