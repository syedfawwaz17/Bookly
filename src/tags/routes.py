from fastapi import APIRouter, Depends, status, HTTPException

from sqlmodel.ext.asyncio.session import AsyncSession

from src.db.main import get_session
from src.auth.dependencies import get_current_user, Rolechecker
from src.db.models import User

from .service import TagService
from .schemas import TagCreateModel, TagUpdateModel, TagModel


tags_router = APIRouter()

tag_service = TagService()


# =====================================
# GET ALL TAGS
# =====================================

@tags_router.get(
    "/",
    response_model=list[TagModel]
)
async def get_all_tags(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    tags = await tag_service.get_all_tags(session)

    return tags


# =====================================
# GET TAG BY UID
# =====================================

@tags_router.get(
    "/{tag_uid}",
    response_model=TagModel
)
async def get_tag(
    tag_uid: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    tag = await tag_service.get_tag_by_uid(
        tag_uid,
        session
    )

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )

    return tag


# =====================================
# CREATE TAG
# =====================================

@tags_router.post(
    "/",
    response_model=TagModel,
    status_code=status.HTTP_201_CREATED
)
async def create_tag(
    tag_data: TagCreateModel,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    new_tag = await tag_service.add_tag(
        tag_data,
        session
    )

    return new_tag


# =====================================
# UPDATE TAG
# =====================================

@tags_router.patch(
    "/{tag_uid}",
    response_model=TagModel
)
async def update_tag(
    tag_uid: str,
    tag_update_data: TagUpdateModel,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    updated_tag = await tag_service.update_tag(
        tag_uid,
        tag_update_data,
        session
    )

    return updated_tag


# =====================================
# DELETE TAG
# =====================================

@tags_router.delete(
    "/{tag_uid}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_tag(
    tag_uid: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):

    await tag_service.delete_tag(
        tag_uid,
        session
    )

    return None