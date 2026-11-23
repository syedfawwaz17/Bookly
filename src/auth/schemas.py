from pydantic import BaseModel,Field
from typing import List
from src.books.schemas import BookModel
from src.reviews.schemas import ReviewModel
import uuid
from datetime import datetime

class UserCreateModel(BaseModel):
    username : str = Field(max_length=25)
    email : str = Field(max_length=25)
    firstname : str
    lastname : str
    password_hash : str = Field(min_length=6)


class UserModel(BaseModel):
    uid : uuid.UUID
    username : str
    email : str
    firstname : str
    lastname : str
    is_verified : bool 
    password_hash : str = Field(exclude=True)
    created_at : datetime 
    updated_at : datetime
    
class UserBooksModel(UserModel):
    books : List[BookModel]
    reviews : List[ReviewModel]

class LoginDataModel(BaseModel):
    email : str = Field(max_length=25)
    password_hash : str = Field(min_length=6)
    
