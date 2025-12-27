from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from starlette import status
from model import Users, AITool, AIToolSchema, Review, ReviewStatus, PricingType
from database import SessionLocal
from routers.auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post("/add-tool", status_code=status.HTTP_201_CREATED)
async def add_tool(
    tool: AIToolSchema,
    db: db_dependency,
    current_user: user_dependency
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db_tool = AITool(**tool.dict())
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool


@router.put("/Update_tool/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_tool(
    tool_id: int = Path(..., description="The ID of the tool to update"),
    tool: AIToolSchema = ...,
    db: db_dependency = ...,
    current_user: user_dependency = ...
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db_tool = db.query(AITool).filter(AITool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

    for key, value in tool.dict(exclude_unset=True).items():
        setattr(db_tool, key, value)

    db.commit()
    return


@router.delete("/delete_tool/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: int = Path(..., description="The ID of the tool to delete"),
    db: db_dependency = ...,
    current_user: user_dependency = ...
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    db_tool = db.query(AITool).filter(AITool.id == tool_id).first()
    if not db_tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

    db.delete(db_tool)
    db.commit()
    return


# ✨ ADVANCED FILTERING ENDPOINT
@router.get("/tools/search", response_model=List[dict], status_code=status.HTTP_200_OK)
async def search_tools(
    category: Optional[str] = Query(None, description="Filter by category (partial match)"),
    pricing_type: Optional[str] = Query(None, description="Filter by pricing type", enum=["FREE", "PAID", "SUBSCRIPTION"]),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Filter by minimum rating (0-5)", enum=[0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]),
    user: user_dependency = ...,
    db: db_dependency = ...
):
    """Advanced search with multiple filters. Accessible to both admin and user.
    
    Query Parameters:
    - category: Optional category name (case-insensitive, partial match)
    - pricing_type: Optional pricing type dropdown (FREE, PAID, SUBSCRIPTION)
    - min_rating: Optional minimum rating dropdown (0-5 in 0.5 increments)
    
    Examples:
    - /tools/search (all tools)
    - /tools/search?category=AI
    - /tools/search?pricing_type=FREE
    - /tools/search?min_rating=4
    - /tools/search?category=AI&pricing_type=FREE&min_rating=4
    """
    
    query = db.query(AITool)
    
    # Apply category filter
    if category:
        query = query.filter(AITool.category.ilike(f"%{category}%"))
    
    # Apply pricing type filter
    if pricing_type:
        try:
            pricing_enum = PricingType[pricing_type.upper()]
            query = query.filter(AITool.pricing_type == pricing_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid pricing type. Must be one of: {', '.join([p.name for p in PricingType])}"
            )
    
    # Apply rating filter
    if min_rating is not None:
        query = query.filter(AITool.avg_rating >= min_rating)
    
    tools = query.all()
    
    if not tools:
        filters_applied = []
        if category:
            filters_applied.append(f"category='{category}'")
        if pricing_type:
            filters_applied.append(f"pricing_type='{pricing_type}'")
        if min_rating is not None:
            filters_applied.append(f"min_rating={min_rating}")
        
        filters_text = ", ".join(filters_applied) if filters_applied else "no filters"
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No tools found with {filters_text}"
        )
    
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