from typing import Annotated, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from model import Users, AITool, AIToolSchema, Review, ReviewStatus, PricingType
from database import SessionLocal
from routers.auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependencies for database and user
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/add_tool", status_code=status.HTTP_201_CREATED)
async def add_tool(
    current_user: user_dependency,
    db: db_dependency,
    tool: AIToolSchema
):
    if current_user['role'].lower() != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db_tool = AITool(**tool.model_dump())  
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool


@router.put("/Update_tool/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_tool(
    tool_id: int = Path(..., description="The ID of the tool to update"),
    tool: AIToolSchema = ...,  # Use the Pydantic schema for validation
    db: db_dependency = ...,
    current_user: user_dependency = ...
):
    if current_user['role'].lower() != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db_tool = db.query(AITool).filter(AITool.id == str(tool_id)).first()
    if not db_tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

    for key, value in tool.dict(exclude_unset=True).items():
        setattr(db_tool, key, value)

    db.commit()
    return {"message": "Tool updated successfully"}


@router.delete("/delete_tool/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: int = Path(..., description="The ID of the tool to delete"),
    db: db_dependency = ...,
    current_user: user_dependency = ...
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db_tool = db.query(AITool).filter(AITool.id == str(tool_id)).first()
    if not db_tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

    db.delete(db_tool)
    db.commit()
    return


# 2️⃣ GET tools by category
@router.get("/tools/category/{category_name}", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_tools_by_category(
    category_name: str,
    user: user_dependency,
    db: db_dependency
):
    """Get all tools filtered by category. Accessible to both admin and user."""
    tools = db.query(AITool).filter(AITool.category.ilike(f"%{category_name}%")).all()
    if not tools:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No tools found for category '{category_name}'")
    return [
        {
            'id': str(t.id),
            'tool_name': t.tool_name,
            'use_case': t.use_case,
            'category': t.category,
            'pricing_type': t.pricing_type.value,
            'avg_rating': t.avg_rating
        }
        for t in tools
    ]


# 3️⃣ GET tools by pricing type
@router.get("/tools/price/{price_type}", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_tools_by_price(
    price_type: str,
    user: user_dependency,
    db: db_dependency
):
    """Get all tools filtered by pricing type. Accessible to both admin and user."""
    # Validate pricing type
    try:
        pricing_enum = PricingType[price_type.upper()]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid pricing type. Must be one of: {', '.join([p.name for p in PricingType])}"
        )
    
    tools = db.query(AITool).filter(AITool.pricing_type == pricing_enum).all()
    if not tools:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No tools found with pricing type '{price_type}'")
    return [
        {
            'id': str(t.id),
            'tool_name': t.tool_name,
            'use_case': t.use_case,
            'category': t.category,
            'pricing_type': t.pricing_type.value,
            'avg_rating': t.avg_rating
        }
        for t in tools
    ]


# 4️⃣ GET tools by minimum rating
@router.get("/tools/rating/{min_rating}", response_model=List[dict], status_code=status.HTTP_200_OK)
async def get_tools_by_rating(
    min_rating: float,
    user: user_dependency,
    db: db_dependency
):
    """Get all tools with rating >= min_rating. Accessible to both admin and user."""
    if min_rating < 0 or min_rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 0 and 5"
        )
    
    tools = db.query(AITool).filter(AITool.avg_rating >= min_rating).all()
    if not tools:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No tools found with rating >= {min_rating}")
    return [
        {
            'id': str(t.id),
            'tool_name': t.tool_name,
            'use_case': t.use_case,
            'category': t.category,
            'pricing_type': t.pricing_type.value,
            'avg_rating': t.avg_rating
        }
        for t in tools
    ]