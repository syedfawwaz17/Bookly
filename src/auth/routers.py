from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from sqlmodel.ext.asyncio.session import AsyncSession

from datetime import timedelta, datetime

from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist

from .service import UserService

from .schemas import (
    UserCreateModel,
    LoginDataModel,
    UserBooksModel
)

from .utils import (
    verify_pass_hash,
    create_access_token,
    generate_pass_hash
)

from .dependencies import (
    RefreshBearerToken,
    AccessTokenBearer,
    get_current_user,
    Rolechecker
)

from src.errors import UserAlreadyExists


# =====================================
# INITIALIZATION
# =====================================

REFRESH_TOKEN_EXPIRY = 2

auth_router = APIRouter()

user_service = UserService()

role_checker = Rolechecker(['admin', 'User'])


# =====================================
# SIGNUP
# =====================================

@auth_router.post(
    '/signup',
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_data: UserCreateModel,
    session: AsyncSession = Depends(get_session)
):

    email = user_data.email

    user_exist = await user_service.user_exist(
        email,
        session
    )

    if user_exist:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(
        user_data,
        session
    )

    # Email verification is no longer required.
    new_user.is_verified = True

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {
        "message": "Account created successfully!",
        "user": new_user
    }


# =====================================
# LOGIN
# =====================================

@auth_router.post('/login')
async def login_user(
    login_data: LoginDataModel,
    session: AsyncSession = Depends(get_session)
):

    email = login_data.email
    password = login_data.password_hash

    user = await user_service.get_user_by_email(
        email,
        session
    )

    if user is not None:

        password_valid = verify_pass_hash(
            password,
            user.password_hash
        )

        if password_valid:

            access_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid),
                    'role': user.role
                }
            )

            refresh_token = create_access_token(
                user_data={
                    'email': user.email,
                    'user_uid': str(user.uid)
                },
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY)
            )

            return JSONResponse(
                content={
                    'message': 'Login successful',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': {
                        'email': user.email,
                        'uid': str(user.uid)
                    }
                },
                status_code=status.HTTP_200_OK
            )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid email or password"
    )


# =====================================
# REFRESH ACCESS TOKEN
# =====================================

@auth_router.get('/refresh_token')
async def get_new_access_token(
    token_data: dict = Depends(RefreshBearerToken())
):

    expiry_timestamp = token_data['exp']

    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():

        new_access_token = create_access_token(
            user_data=token_data['user']
        )

        return JSONResponse(
            content={
                "access_token": new_access_token
            },
            status_code=status.HTTP_200_OK
        )

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Refresh token expired"
    )


# =====================================
# GET CURRENT USER
# =====================================

@auth_router.get(
    '/me',
    response_model=UserBooksModel
)
async def read_current_user(
    user=Depends(get_current_user),
    _: bool = Depends(role_checker)
):

    return user


# =====================================
# LOGOUT
# =====================================

@auth_router.get('/logout')
async def revoke_token(
    token_details: dict = Depends(AccessTokenBearer())
):

    jti = token_details['jti']

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={
            "message": "Successfully logged out"
        },
        status_code=status.HTTP_200_OK
    )