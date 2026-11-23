
import ssl

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel

from src.config import Config


# SSL Configuration
#ssl_context = ssl.create_default_context()


# Database Engine
engine = create_async_engine(
    Config.DATABASE_URL,
   # connect_args={
    #    "ssl": ssl_context
    #},
    pool_pre_ping=True,
    pool_recycle=300
)


# Session Factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Initialize Database
async def init_db():
    async with engine.begin() as conn:

        from src.db.models import Book
        from src.db.models import User

        await conn.run_sync(SQLModel.metadata.create_all)


# Database Dependency
async def get_session():

    async with SessionLocal() as session:
        yield session
