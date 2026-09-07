from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import (
    require_admin,
    require_admin_or_staff
)

from app.models.user import User

from app.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductSummaryResponse,
    ProductUpdate,
    StockAdjustment,
)

from app.controllers import product_controller

from app.utils.constraints import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
)
import uuid

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return product_controller.create_product(
        db,
        data
    )


@router.get(
    "/summary",
    response_model=ProductSummaryResponse
)
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_staff)
):
    return product_controller.get_product_summary(db)


@router.get(
    "/",
    response_model=ProductListResponse
)
def get_products(
    page: int = Query(
        DEFAULT_PAGE,
        ge=1
    ),
    page_size: int = Query(
        DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE
    ),
    search: str | None = None,
    category_id: uuid.UUID | None = Query(
        default=None
    ),
    stock_status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_staff)
):
    return product_controller.get_products(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        stock_status=stock_status
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
def get_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends
    (require_admin_or_staff)
):
    return product_controller.get_product(
        db=db,
        product_id=product_id
    )


@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return product_controller.update_product(
        db,
        product_id,
        data
    )


@router.patch(
    "/{product_id}/stock",
    response_model=ProductResponse
)
def adjust_stock(
    product_id: uuid.UUID,
    data: StockAdjustment,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return product_controller.adjust_stock(
        db,
        product_id,
        data,
        
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_product(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    product_controller.delete_product(
        db,
        product_id,
    )