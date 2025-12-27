import enum
from uuid import uuid4
from sqlalchemy import Column, Float, Integer, String, Text, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from database import Base

# User Model

class Users(Base):
    __tablename__ = 'users'
 
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    role = Column(String)
    

# Tool Model

class PricingType(enum.Enum):

    FREE = "FREE"
    PAID = "PAID"
    SUBSCRIPTION = "SUBSCRIPTION"

    # Review Status Enum

class ReviewStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"

class AITool(Base):

    __tablename__ = "ai_tools"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tool_name = Column(String(150), nullable=False, index=True)
    use_case = Column(Text)
    category = Column(String(100), index=True)
    pricing_type = Column(enum.Enum(PricingType), nullable=False)
    avg_rating = Column(Float, default=0.0)


# Review Modelclass Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(Integer, nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    status = Column(enum.Enum(ReviewStatus), default=ReviewStatus.PENDING)
    
 

 
 