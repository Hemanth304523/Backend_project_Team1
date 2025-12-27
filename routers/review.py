from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from model import Users, AITool, Review, ReviewStatus
from database import SessionLocal
from .auth import get_current_user
 
router = APIRouter(
    prefix='/user',
    tags=['user']
)
 
 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()