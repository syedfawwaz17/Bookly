from fastapi import Request, status, Depends
from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from src.errors import AccountNotVerified
from .utils import decode_token

from src.db.redis import token_in_blocklist
from src.db.main import get_session

from sqlmodel.ext.asyncio.session import AsyncSession

from .service import UserService
from src.db.models import User

from typing import List


user_service = UserService()


# =====================================
# TOKEN BEARER
# =====================================

class TokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):

        creds = await super().__call__(request)

        if creds is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials missing"
            )

        token = creds.credentials

        token_data = decode_token(token)

        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token"
            )

        # Redis blocklist verification
        if await token_in_blocklist(token_data['jti']):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This token has been revoked"
            )

        self.verify_token(token_data)

        return token_data

    def verify_token(self, token_data: dict):

        raise NotImplementedError(
            "Override this method"
        )


# =====================================
# ACCESS TOKEN
# =====================================

class AccessTokenBearer(TokenBearer):

    def verify_token(self, token_data: dict):

        if token_data.get('refresh') is True:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide an access token"
            )


# =====================================
# REFRESH TOKEN
# =====================================

class RefreshBearerToken(TokenBearer):

    def verify_token(self, token_data: dict):

        if token_data.get('refresh') is not True:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please provide a refresh token"
            )


# =====================================
# GET CURRENT USER
# =====================================

async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session)
):

    user_email = token_details['user']['email']

    user = await user_service.get_user_by_email(
        user_email,
        session
    )

    if user is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


# =====================================
# ROLE BASED ACCESS CONTROL
# =====================================

class Rolechecker:

    def __init__(self, allowed_roles: List[str]):

        # Normalize allowed roles
        self.allowed_roles = [
            role.lower() for role in allowed_roles
        ]

    def __call__(
        self,
        current_user: User = Depends(get_current_user)
    ):
        if not current_user.is_verified:
            raise AccountNotVerified()

        # Normalize database user role
        user_role = current_user.role.lower()

        if user_role in self.allowed_roles:
            return True

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to perform this action"
        )