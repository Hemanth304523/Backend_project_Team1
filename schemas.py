from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from model import PricingType, ReviewStatus

class AIToolSchema(BaseModel):
    tool_name: str = Field(..., min_length=1, max_length=150)
    use_case: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = Field(None, max_length=100)
    pricing_type: PricingType = Field(...)
    avg_rating: Optional[float] = Field(0.0, ge=0.0, le=5.0)

class ReviewSchema(BaseModel):
    tool_id: str = Field(..., min_length=1)
    user_rating: int = Field(..., ge=1, le=5, description="Rating between 1 and 5")
    comment: Optional[str] = Field(None, max_length=1000)

class ReviewResponseSchema(ReviewSchema):
    id: int
    user_id: int
    approval_status: ReviewStatus

    model_config = {"from_attributes": True}


class AIToolResponseSchema(BaseModel):
    id: str
    tool_name: str
    use_case: Optional[str] = None
    category: Optional[str] = None
    pricing_type: PricingType
    avg_rating: float

    model_config = {"from_attributes": True}

class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=6)
    role: Literal['user', 'admin', 'USER', 'ADMIN']

class Token(BaseModel):
    access_token: str
    token_type: str

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)