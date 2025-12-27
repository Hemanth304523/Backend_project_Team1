import enum
from uuid import uuid4
from database import Base
from sqlalchemy import Column, Float, Integer, String, Text, Enum as SqlEnum


# Users Table
class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)


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


# AI Tool Table
class AITool(Base):
    __tablename__ = "ai_tools"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))  # Use String for UUID compatibility
    tool_name = Column(String(150), nullable=False, index=True)
    use_case = Column(Text)
    category = Column(String(100), index=True)
    pricing_type = Column(SqlEnum(PricingType), nullable=False)
    avg_rating = Column(Float, default=0.0)


# Review Table
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(String, nullable=False)  # Use String for UUID compatibility
    user_id = Column(Integer, nullable=False)
    user_rating = Column(Integer, nullable=False)
    comment = Column(Text)
    approval_status = Column(SqlEnum(ReviewStatus), default=ReviewStatus.PENDING)