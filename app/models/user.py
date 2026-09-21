from sqlalchemy import Column, ForeignKey, String, UUID
from app.core.database import Base
import uuid 
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True,   default=uuid.uuid4,)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)
    manager_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    manager = relationship(
        "User",
        remote_side=[id],
        back_populates="staff_members",
    )
    staff_members = relationship(
        "User",
        back_populates="manager",
    )