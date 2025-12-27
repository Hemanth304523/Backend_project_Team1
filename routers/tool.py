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

