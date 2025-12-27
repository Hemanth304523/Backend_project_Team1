from typing import Annotated, List
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, status, Query
from model import AITool, Review, ReviewStatus
from schemas import ReviewSchema, ReviewResponseSchema, AIToolResponseSchema
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


@router.post('/add_review', status_code=status.HTTP_201_CREATED, response_model=ReviewResponseSchema)
def add_review(
    current_user: user_dependency,
    db: db_dependency,
    review_data: ReviewSchema
):
    """Add a new review for an AI tool"""
    
    tool = db.query(AITool).filter(AITool.id == review_data.tool_id).first()
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tool not found')
    
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
    
    review_out = ReviewResponseSchema(
        id=new_review.id,
        tool_id=new_review.tool_id,
        user_id=new_review.user_id,
        user_rating=new_review.user_rating,
        comment=new_review.comment,
        approval_status=new_review.approval_status
    )
    return review_out


@router.get('/reviews/pending', status_code=status.HTTP_200_OK, response_model=List[ReviewResponseSchema])
def get_pending_reviews(
    current_user: user_dependency,
    db: db_dependency
) -> List[ReviewResponseSchema]:
    if current_user['role'].lower() == 'admin':
        pending = db.query(Review).filter(Review.approval_status == ReviewStatus.PENDING)
    elif current_user['role'].lower() == 'user':
        pending = db.query(Review).filter(Review.user_id == current_user['id']).filter(Review.approval_status == ReviewStatus.PENDING)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource')
    return pending.all()


@router.get('/reviews/approved', status_code=status.HTTP_200_OK, response_model=List[ReviewResponseSchema])
def get_approved_reviews(
    current_user: user_dependency,
    db: db_dependency
) -> List[ReviewResponseSchema]:
    if current_user['role'].lower() == 'admin':
        approved = db.query(Review).filter(Review.approval_status == ReviewStatus.APPROVED)
    elif current_user['role'].lower() == 'user':
        approved = db.query(Review).filter(Review.user_id == current_user['id']).filter(Review.approval_status == ReviewStatus.APPROVED)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource')
    return approved.all()


@router.get('/all_reviews', status_code=status.HTTP_200_OK, response_model=List[ReviewResponseSchema])
def get_all_reviews(
    current_user: user_dependency,
    db: db_dependency
) -> List[ReviewResponseSchema]:
    if current_user['role'].lower() == 'admin':
        all = db.query(Review)
    elif current_user['role'].lower() == 'user':
        all = db.query(Review).filter(Review.user_id == current_user['id'])
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Not authorized to access this resource')
    return all.all()


@router.patch("/approve_review/{review_id}", status_code=status.HTTP_200_OK)
async def moderate_review(
    current_user: user_dependency,
    db: db_dependency,
    review_id: int = Path(..., description="The ID of the review to moderate"),
    approval_status: ReviewStatus = Query(..., description="New approval status (APPROVED, REJECTED, PENDING)")
):
    """Update review approval status and recalibrate tool rating"""
    
    if current_user['role'].lower() != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    review.approval_status = approval_status
    db.commit()
    db.refresh(review)

    tool = db.query(AITool).filter(AITool.id == review.tool_id).first()
    if not tool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")

    approved_reviews = db.query(Review).filter(
        Review.tool_id == tool.id,
        Review.approval_status == ReviewStatus.APPROVED
    ).all()

    if approved_reviews:
        tool.avg_rating = sum(r.user_rating for r in approved_reviews) / len(approved_reviews)
    else:
        tool.avg_rating = 0.0

    db.commit()
    db.refresh(tool)

    review_out = ReviewResponseSchema(
        id=review.id,
        tool_id=review.tool_id,
        user_id=review.user_id,
        user_rating=review.user_rating,
        comment=review.comment,
        approval_status=review.approval_status
    )

    tool_out = AIToolResponseSchema(
        id=str(tool.id),
        tool_name=tool.tool_name,
        use_case=tool.use_case,
        category=tool.category,
        pricing_type=tool.pricing_type,
        avg_rating=tool.avg_rating
    )

    return {
        "message": f"Review {approval_status.value.lower()} successfully",
        "review": review_out,
        "tool_updated": tool_out
    }




