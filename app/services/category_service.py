from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,)
from app.utils.exceptions import (
    ConflictException,
    NotFoundException,)


def create_category(
    db: Session,
    data: CategoryCreate):
    existing = db.scalar(
        select(Category).where(
            Category.name == data.name))

    if existing:
        raise ConflictException(
            "Category with this name already exists" )

    category = Category(
        name=data.name,
        description=data.description)

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


def get_categories(db: Session):
    return db.scalars(
        select(Category)
        .order_by(Category.id)).all()


def update_category(
    db: Session,
    category_id: int,
    data: CategoryUpdate):
    category = db.get(
        Category,
        category_id)

    if not category:
        raise NotFoundException(
            "Category not found")

    if data.name is not None:
        existing = db.scalar(
            select(Category).where(
                Category.name == data.name,
                Category.id != category_id ))

        if existing:
            raise ConflictException(
                "Category with this name already exists")

        category.name = data.name

    if data.description is not None:
        category.description = data.description

    db.commit()
    db.refresh(category)

    return category


def delete_category(
    db: Session,
    category_id: int):
    category = db.get(
        Category,
        category_id)

    if not category:
        raise NotFoundException(
            "Category not found")

    if category.products:
        raise ConflictException(
            "Cannot delete category because products are linked to it")

    db.delete(category)
    db.commit()