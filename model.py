import enum
from uuid import uuid4
from database import Base
from sqlalchemy import UUID, Column, Float, Integer, String, Boolean, ForeignKey, Text
import enum
from uuid import uuid4
from datetime import datetime
 
from sqlalchemy import Column, Integer, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
 
from database import Base
 
class Users(Base):
    __tablename__ = 'users'
 
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    role = Column(String)
    
class PricingType(enum.Enum):

    FREE = "FREE"
    PAID = "PAID"
    SUBSCRIPTION = "SUBSCRIPTION"
class AITool(Base):

    __tablename__ = "ai_tools"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tool_name = Column(String(150), nullable=False, index=True)
    use_case = Column(Text)
    category = Column(String(100), index=True)
    pricing_type = Column(enum.Enum(PricingType), nullable=False)
    avg_rating = Column(Float, default=0.0)

 
class ReviewStatus(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
 
class Review(Base):
    __tablename__ = "reviews"
 
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
 
    tool_id = Column(UUID(as_uuid=True), ForeignKey("ai_tools.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
 
    user_rating = Column(Integer, nullable=False)
    comment = Column(Text)
    approval_status = Column(Enum(ReviewStatus), default=ReviewStatus.PENDING)
 
 
 
 