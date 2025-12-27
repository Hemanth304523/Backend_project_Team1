from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from model import Users, AITool, Review, ReviewStatus
from database import SessionLocal
from .auth import get_current_user
 
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
    tool: AITool,
    db: db_dependency,
    current_user: user_dependency
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return tool

@router.patch("/approve_review/{review_id}", status_code=status.HTTP_200_OK)
async def moderate_review(
    review_id: int,
    approval_status: ReviewStatus,
    db: db_dependency,
    current_user: user_dependency
):
    # Ensure the user is an admin
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    # Fetch the review by ID
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    # Update the review's approval status
    review.status = approval_status
    db.commit()
    db.refresh(review)

    # Recalculate the average rating for the associated tool if the review is approved
    if approval_status == ReviewStatus.APPROVED:
        tool = db.query(AITool).filter(AITool.id == review.tool_id).first()
        if not tool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

        # Fetch all approved reviews for the tool
        approved_reviews = db.query(Review).filter(
            Review.tool_id == tool.id,
            Review.status == ReviewStatus.APPROVED
        ).all()

        # Calculate the new average rating
        if approved_reviews:
            tool.avg_rating = sum(r.rating for r in approved_reviews) / len(approved_reviews)
        else:
            tool.avg_rating = 0.0  # No approved reviews, reset to 0

        db.commit()
        db.refresh(tool)

    return {"message": f"Review {approval_status.value.lower()}", "review": review}

@router.put("/Update_tool/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_tool(
    tool_id: int = Path(..., description="The ID of the tool to update"),
    tool: AITool = ...,
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

