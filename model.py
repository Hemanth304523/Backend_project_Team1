import enum
from uuid import uuid4
from database import Base
from sqlalchemy import UUID, Column, Float, Integer, String, Boolean, ForeignKey, Text
 
 
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
 