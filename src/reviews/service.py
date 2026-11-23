from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc

from .schemas import ReviewCreateModel
from fastapi import HTTPException, status

from src.books.service import BookService
from src.auth.service import UserService
from src.db.models import Review

import logging

book_service = BookService()
user_service = UserService()


class ReviewService:

    # =====================================
    # ADD REVIEW TO BOOK
    # =====================================

    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreateModel,
        session: AsyncSession
    ):

        try:
            book = await book_service.get_book(
                book_uid=book_uid,
                session=session
            )

            user = await user_service.get_user_by_email(
                email=user_email,
                session=session
            )

            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            review_data_dict = review_data.model_dump()

            new_review = Review(**review_data_dict)

            new_review.user = user
            new_review.book = book

            session.add(new_review)

            await session.commit()
            await session.refresh(new_review)

            return new_review

        except HTTPException:
            raise

        except Exception as e:
            await session.rollback()
            logging.exception(e)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Something went wrong"
            )

    # =====================================
    # GET REVIEW BY UID
    # =====================================

    async def get_review_by_uid(
        self,
        review_uid: str,
        session: AsyncSession
    ):

        statement = select(Review).where(
            Review.uid == review_uid
        )

        result = await session.exec(statement)

        return result.first()

    # =====================================
    # GET ALL USER REVIEWS
    # =====================================

    async def get_user_reviews(
        self,
        user_uid: str,
        session: AsyncSession
    ):

        statement = (
            select(Review)
            .where(Review.user_uid == user_uid)
            .order_by(desc(Review.created_at))
        )

        result = await session.exec(statement)

        return result.all()

    # =====================================
    # DELETE USER REVIEW
    # =====================================

    async def delete_user_review(
        self,
        review_uid: str,
        user_uid: str,
        session: AsyncSession
    ):

        statement = select(Review).where(
            Review.uid == review_uid,
            Review.user_uid == user_uid
        )

        result = await session.exec(statement)

        review = result.first()

        if review is None:
            return None

        await session.delete(review)

        await session.commit()

        return review