from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from .service import BookService
from .schemas import BookCreateModel, BookUpdateModel, BookReviewModel
from src.db.models import Book

from src.errors import BookNotFound

from src.db.main import get_session
from src.auth.dependencies import (
    AccessTokenBearer,
    Rolechecker
)


# Initialize dependencies
bearer_token = AccessTokenBearer()

role_checker = Rolechecker(['admin', 'user'])


# Apply authentication and authorization
book_router = APIRouter(
    dependencies=[
        Depends(bearer_token),
        Depends(role_checker)
    ]
)

book_service = BookService()


# =====================================
# GET ALL BOOKS
# =====================================

@book_router.get(
    '/',
    response_model=list[Book],
    status_code=status.HTTP_200_OK
)
async def get_all_books(
    session: AsyncSession = Depends(get_session)
):

    books = await book_service.get_all_books(session)

    return books


# =====================================
# GET BOOKS BY USER
# =====================================

@book_router.get(
    '/user/{user_uid}',
    response_model=list[BookReviewModel],
    status_code=status.HTTP_200_OK
)
async def get_user_book_submissions(
    user_uid: str,
    session: AsyncSession = Depends(get_session)
):

    books = await book_service.get_user_books(
        user_uid,
        session
    )

    return books


# =====================================
# CREATE A BOOK
# =====================================

@book_router.post(
    '/',
    response_model=Book,
    status_code=status.HTTP_201_CREATED
)
async def create_book(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(bearer_token)
):

    user_id = token_details['user']['user_uid']

    book = await book_service.create_book(
        book_data,
        user_id,
        session
    )

    return book


# =====================================
# GET BOOK BY UID
# =====================================

@book_router.get(
    '/{book_uid}',
    response_model=Book,
    status_code=status.HTTP_200_OK
)
async def get_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session)
):

    book = await book_service.get_book(
        book_uid,
        session
    )

    if book is None:
        raise BookNotFound()

    return book


# =====================================
# UPDATE BOOK
# =====================================

@book_router.patch(
    '/{book_uid}',
    response_model=Book,
    status_code=status.HTTP_200_OK
)
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session)
):

    book = await book_service.update_book(
        book_uid,
        book_update_data,
        session
    )

    if book is None:
        raise BookNotFound()

    return book


# =====================================
# DELETE BOOK
# =====================================

@book_router.delete(
    '/{book_uid}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session)
):

    book = await book_service.delete_book(
        book_uid,
        session
    )

    if book is None:
        raise BookNotFound()

    return None