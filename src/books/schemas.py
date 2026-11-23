from pydantic import BaseModel, ConfigDict
from typing import Optional,List
from datetime import date, datetime
import uuid
from src.reviews.schemas import ReviewModel


# CREATE BOOK
class BookCreateModel(BaseModel):

    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str


# UPDATE BOOK
class BookUpdateModel(BaseModel):

    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None


# BOOK RESPONSE MODEL
class BookModel(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    
    
class BookReviewModel(BookModel):
    reviews : List[ReviewModel]