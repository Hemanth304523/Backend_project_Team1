from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from starlette import status
from model import Users, AITool, Review, ReviewStatus, ReviewSchema, ReviewResponseSchema
from database import SessionLocal
from .auth import get_current_user
 
router = APIRouter(
    prefix='/admin',
    tags=['review']
)
 
 
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
 
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.post('/add_review', response_model=dict, status_code=status.HTTP_201_CREATED)
def add_review(
    review_data: ReviewSchema,
    db: db_dependency,
    current_user: user_dependency
):
    """Add a new review for an AI tool"""
    
    # Verify that the tool exists
    tool = db.query(AITool).filter(AITool.id == review_data.tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tool not found'
        )
    
    # Create new review
    new_review = Review(
        tool_id=review_data.tool_id,
        user_id=current_user['id'],
        user_rating=review_data.user_rating,
        comment=review_data.comment,
        approval_status=ReviewStatus.PENDING
    )
    
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    
    return {
        'id': new_review.id,
        'tool_id': str(new_review.tool_id),
        'user_id': new_review.user_id,
        'user_rating': new_review.user_rating,
        'comment': new_review.comment,
        'approval_status': new_review.approval_status.value,
        'message': 'Review submitted successfully and is pending approval'
    }


@router.get('/reviews/pending', response_model=list[dict])
def get_pending_reviews(
    db: db_dependency,
    current_user: user_dependency
):
    if current_user['role'] == 'admin':
        pending_reviews = db.query(Review).filter(Review.approval_status == ReviewStatus.PENDING).all()
    elif current_user['role'] == 'user':
        pending_reviews=db.query(Review).filter(Review.user_id==current_user['id']).filter(Review.approval_status == ReviewStatus.PENDING).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to access this resource'
        )
    return [
        {
            'id': review.id,
            'tool_id': review.tool_id,
            'user_id': review.user_id,
            'user_rating': review.user_rating,
            'comment': review.comment,
            'approval_status': review.approval_status.value
        }
        for review in pending_reviews
    ]

@router.get('/reviews/aproved')
def get_approved_reviews(
    db: db_dependency,
    current_user: user_dependency
):
    if current_user['role'] == 'admin':
        approved_reviews = db.query(Review).filter(Review.approval_status == ReviewStatus.APPROVED).all()
    elif current_user['role'] == 'user':
        approved_reviews=db.query(Review).filter(Review.user_id==current_user['id']).filter(Review.approval_status == ReviewStatus.APPROVED).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to access this resource'
        )   
    return [
        {
            'id': review.id,
            'tool_id': review.tool_id,
            'user_id': review.user_id,
            'user_rating': review.user_rating,
            'comment': review.comment,
            'approval_status': review.approval_status.value
        }
        for review in approved_reviews
    ]
@router.get('/all_reviews')
def get_all_reviews(
    db: db_dependency,
    current_user: user_dependency
):
    if current_user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to access this resource'
        )

    all_reviews = db.query(Review).all()

    return [
        {
            'id': review.id,
            'tool_id': review.tool_id,
            'user_id': review.user_id,
            'user_rating': review.user_rating,
            'comment': review.comment,
            'approval_status': review.approval_status.value
        }
        for review in all_reviews
    ]


@router.patch("/approve_review/{review_id}", status_code=status.HTTP_200_OK)
async def moderate_review(
    review_id: int,
    approval_status: ReviewStatus,
    db: db_dependency,
    current_user: user_dependency
):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    review.approval_status = approval_status
    db.commit()
    db.refresh(review)

    if approval_status == ReviewStatus.APPROVED:
        tool = db.query(AITool).filter(AITool.id == review.tool_id).first()
        if not tool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

        approved_reviews = db.query(Review).filter(
            Review.tool_id == tool.id,
            Review.approval_status == ReviewStatus.APPROVED
        ).all()

        tool.avg_rating = sum(r.rating for r in approved_reviews) / len(approved_reviews) if approved_reviews else 0.0
        db.commit()
        db.refresh(tool)

    return {"message": f"Review {approval_status.value.lower()}", "review": review}

@router.patch('/reject_review/{review_id}', status_code=status.HTTP_200_OK)
def reject_review(
    review_id: int,
    db: db_dependency,
    current_user: user_dependency
):
    if current_user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authorized to access this resource'
        )

    review = db.query(Review).filter(Review.id == review_id).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found'
        )

    review.approval_status = ReviewStatus.REJECTED
    # Recalculate average rating for the tool
    tool = db.query(AITool).filter(AITool.id == review.tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Tool not found'
        )
    approved_reviews = db.query(Review).filter(
        Review.tool_id == tool.id,
        Review.approval_status == ReviewStatus.APPROVED
    ).all()
    if approved_reviews:
        tool.avg_rating = sum(r.user_rating for r in approved_reviews) / len(approved_reviews)
    else:
        tool.avg_rating = 0.0  # No approved reviews left
    db.commit()
    db.refresh(review)

    return {
        'id': review.id,
        'tool_id': review.tool_id,
        'user_id': review.user_id,
        'user_rating': review.user_rating,
        'comment': review.comment,
        'approval_status': review.approval_status.value
    }



   