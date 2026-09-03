from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from app.schemas.product import (ProductCreate, ProductUpdate,StockAdjustment,)

from app.services import product_service

from app.utils.exceptions import (
    ConflictException,
    NotFoundException,
)


def create_product(
    db: Session,
    data: ProductCreate
):
    try:
        product = product_service.create_product(
            db,
            data
        )

        return add_stock_status(product)

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )

    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )


def get_product_summary(
    db: Session
):
    return product_service.get_product_summary(db)


def get_products(
    db: Session,
    page: int,
    page_size: int,
    search: str | None = None,
    category_id: int | None = None,
    stock_status: str | None = None
):
    result = product_service.get_products(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        stock_status=stock_status
    )

    result["items"] = [
        add_stock_status(product)
        for product in result["items"]
    ]

    return result


def get_product(
    db: Session,
    product_id: int
):
    try:
        product = product_service.get_product(
            db,
            product_id
        )

        return add_stock_status(product)

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


def update_product(
    db: Session,
    product_id: int,
    data: ProductUpdate
):
    try:
        product = product_service.update_product(
            db,
            product_id,
            data
        )

        return add_stock_status(product)

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )

    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )


def adjust_stock(
    db: Session,
    product_id: int,
    data: StockAdjustment
):
    try:
        product = product_service.adjust_stock(
            db,
            product_id,
            data
        )

        return add_stock_status(product)

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )

    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )


def delete_product(
    db: Session,
    product_id: int
):
    try:
        product_service.delete_product(
            db,
            product_id
        )

    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )


def add_stock_status(product):
    product.stock_status = product_service.calculate_stock_status(
        product.quantity_in_stock,
        product.reorder_level
    )

    return product