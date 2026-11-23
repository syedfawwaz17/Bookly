from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.db.models import User
from .schemas import UserCreateModel
from .utils import generate_pass_hash
class UserService:
    async def get_user_by_email(self,email:str,session:AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        return result.first()
    async def user_exist(self,email:str,session:AsyncSession):
        user = await self.get_user_by_email(email,session)
        return False if user is None else True

    async def create_user(self,user_data:UserCreateModel,session:AsyncSession):
        user_data_dict = user_data.model_dump()
        new_data = User(
            **user_data_dict
        )
        new_data.password_hash=generate_pass_hash(user_data_dict['password_hash'])
        new_data.role = "User"

        session.add(new_data)
        await session.commit()
        await session.refresh(new_data)
        return new_data
    
    async def update_user(
        self,
        user: User,
        user_data: dict,
        session: AsyncSession
    ):
        for k, v in user_data.items():
            setattr(user, k, v)

        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user