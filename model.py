import enum
from uuid import uuid4
from database import Base
from sqlalchemy import UUID, Column, Float, Integer, String, Text, Enum as SqlEnum
from pydantic import BaseModel
from typing import Optional


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    role = Column(String)


# Pricing Type Enum
class PricingType(enum.Enum):
    FREE = "FREE"
    PAID = "PAID"
    SUBSCRIPTION = "SUBSCRIPTION"


# Review Status Enum
class ReviewStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# AI Tool Model
class AITool(Base):
    __tablename__ = "ai_tools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tool_name = Column(String(150), nullable=False, index=True)
    use_case = Column(Text)
    category = Column(String(100), index=True)
    pricing_type = Column(SqlEnum(PricingType), nullable=False)
    avg_rating = Column(Float, default=0.0)


# Review Model
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(Integer, nullable=False)
    user_rating = Column(Integer, nullable=False)
    comment = Column(Text)
    approval_status = Column(SqlEnum(ReviewStatus), default=ReviewStatus.PENDING)


# Pydantic Schema for AITool
class AIToolSchema(BaseModel):
    tool_name: str
    use_case: Optional[str]
    category: Optional[str]
    pricing_type: PricingType
    avg_rating: Optional[float] = 0.0

    class Config:
        orm_mode = True