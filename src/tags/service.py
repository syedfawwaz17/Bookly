from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from src.db.models import Tag
from .schemas import TagCreateModel, TagUpdateModel

from fastapi import HTTPException, status


class TagService:

    # =====================================
    # GET TAG BY UID
    # =====================================

    async def get_tag_by_uid(
        self,
        tag_uid: str,
        session: AsyncSession
    ):

        statement = select(Tag).where(Tag.uid == tag_uid)

        result = await session.exec(statement)

        return result.first()

    # =====================================
    # GET ALL TAGS
    # =====================================

    async def get_all_tags(
        self,
        session: AsyncSession
    ):

        statement = select(Tag)

        result = await session.exec(statement)

        return result.all()

    # =====================================
    # CREATE TAG
    # =====================================

    async def add_tag(
        self,
        tag_data: TagCreateModel,
        session: AsyncSession
    ):

        tag_data_dict = tag_data.model_dump()

        new_tag = Tag(**tag_data_dict)

        session.add(new_tag)

        await session.commit()

        await session.refresh(new_tag)

        return new_tag

    # =====================================
    # UPDATE TAG
    # =====================================

    async def update_tag(
        self,
        tag_uid: str,
        tag_update_data: TagUpdateModel,
        session: AsyncSession
    ):

        tag = await self.get_tag_by_uid(
            tag_uid,
            session
        )

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        update_data_dict = tag_update_data.model_dump(
            exclude_unset=True
        )

        for k, v in update_data_dict.items():
            setattr(tag, k, v)

        await session.commit()

        await session.refresh(tag)

        return tag

    # =====================================
    # DELETE TAG
    # =====================================

    async def delete_tag(
        self,
        tag_uid: str,
        session: AsyncSession
    ):

        statement = select(Tag).where(
            Tag.uid == tag_uid
        )

        result = await session.exec(statement)

        tag = result.first()

        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )

        await session.delete(tag)

        await session.commit()

        return None