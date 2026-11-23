from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from src.db.models import Book
from .schemas import BookCreateModel, BookUpdateModel
from datetime import datetime


class BookService:

    # GET ALL BOOKS
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()
    
    # GET ALL BOOKS
    async def get_user_books(self, user_uid : str ,session: AsyncSession):
        statement = select(Book).where(Book.user_uid == user_uid).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()
    # GET BOOK BY UID
    async def get_book(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book if book is not None else None

    # CREATE BOOK
    async def create_book(
        self,
        book_data: BookCreateModel,
        user_uid: str,
        session: AsyncSession
    ):
        book_create_dict = book_data.model_dump()

        new_book = Book(**book_create_dict)

        new_book.user_uid = user_uid

        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)

        return new_book

    # UPDATE BOOK
    async def update_book(
        self,
        book_uid: str,
        update_data: BookUpdateModel,
        session: AsyncSession
    ):
        book_to_update = await self.get_book(book_uid, session)

        if not book_to_update:
            return None

        book_update_dict = update_data.model_dump(exclude_unset=True)

        for k, v in book_update_dict.items():
            setattr(book_to_update, k, v)

        await session.commit()
        await session.refresh(book_to_update)

        return book_to_update

    # DELETE BOOK
    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book(book_uid, session)

        if book_to_delete is None:
            return None

        await session.delete(book_to_delete)
        await session.commit()

        return book_to_delete