from fastapi import APIRouter, Depends, HTTPException, status

from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.dependencies import get_current_user
from src.db.main import get_session
from src.db.models import User

from .schemas import ReviewCreateModel, ReviewModel
from .service import ReviewService


review_router = APIRouter()

review_service = ReviewService()

# =====================================
# GET ALL USER REVIEWS
# =====================================

@review_router.get(
    "/user",
    response_model=list[ReviewModel]
)
async def get_user_reviews(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):

    reviews = await review_service.get_user_reviews(
        current_user.uid,
        session
    )

    return reviews


# =====================================
# GET REVIEW BY UID
# =====================================

@review_router.get(
    "/{review_uid}",
    response_model=ReviewModel
)
async def get_review(
    review_uid: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):

    review = await review_service.get_review_by_uid(
        review_uid,
        session
    )

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    return review




# =====================================
# DELETE USER REVIEW BY UID
# =====================================

@review_router.delete(
    "/{review_uid}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user_review(
    review_uid: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):

    review = await review_service.delete_user_review(
        review_uid,
        current_user.uid,
        session
    )

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )

    return None


# =====================================
# ADD REVIEW TO A BOOK
# =====================================

@review_router.post(
    "/book/{book_uid}",
    response_model=ReviewModel,
    status_code=status.HTTP_201_CREATED
)
async def add_review_to_book(
    book_uid: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):

    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        book_uid=book_uid,
        review_data=review_data,
        session=session
    )

    return new_review