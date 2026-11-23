from fastapi import APIRouter, status, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse

from sqlmodel.ext.asyncio.session import AsyncSession

from datetime import timedelta, datetime

from src.config import Config
from src.db.main import get_session
from src.db.redis import add_jti_to_blocklist

from fastapi import APIRouter, status, Depends, BackgroundTasks

from src.email_tasks import send_email_background

from .service import UserService

from .schemas import (
    UserCreateModel,
    LoginDataModel,
    UserBooksModel,
    EmailModel,
    PasswordResetConfirm,
    PasswordReset
)

from .utils import (
    verify_pass_hash,
    create_access_token,
    create_url_safe_token,
    decode_url_self_token,
    generate_pass_hash
)

from .dependencies import (
    RefreshBearerToken,
    AccessTokenBearer,
    get_current_user,
    Rolechecker
)

from src.errors import UserAlreadyExists, UserNotFound


# =====================================
# INITIALIZATION
# =====================================

REFRESH_TOKEN_EXPIRY = 2

auth_router = APIRouter()

user_service = UserService()

role_checker = Rolechecker(['admin', 'User'])


# =====================================
# SEND EMAIL
# =====================================

@auth_router.post('/send_email')
async def send_email(
    emails: EmailModel,
    background_tasks: BackgroundTasks
):

    recipients = emails.addresses

    html = "<h1>Welcome to Bookly</h1>"

    background_tasks.add_task(
        send_email_background,
        recipients,
        "Welcome",
        html
    )

    return {
        "message": "Email has been scheduled successfully"
    }

# =====================================
# SIGNUP
# =====================================

@auth_router.post(
    '/signup',
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_data: UserCreateModel,
     background_tasks: BackgroundTasks,
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

    # Generate email verification token
    token = create_url_safe_token({
        "email": email
    })

    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    html_message = f"""
    <h1>Verify your email</h1>

    <p>Please click the link below to verify your account:</p>

    <a href="{link}">Verify Email</a>
    """

    
    background_tasks.add_task(
    send_email_background,
    [email],
    "Verify Your Email",
    html_message
    )

    return {
        "message": "Account created! Check your email to verify your account",
        "user": new_user
    }


# =====================================
# EMAIL VERIFICATION
# =====================================

@auth_router.get('/verify/{token}')
async def verify_token(
    token: str,
    session: AsyncSession = Depends(get_session)
):

    token_data = decode_url_self_token(token)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )

    user_email = token_data.get('email')

    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    user = await user_service.get_user_by_email(
        user_email,
        session
    )

    if not user:
        raise UserNotFound()

    if user.is_verified:
        return {
            "message": "Email already verified"
        }

    await user_service.update_user(
        user,
        {"is_verified": True},
        session
    )

    return JSONResponse(
        content={
            "message": "Email verified successfully"
        },
        status_code=status.HTTP_200_OK
    )


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


# =====================================
# PASSWORD RESET REQUEST
# =====================================

@auth_router.post("/password-reset-request")
async def password_reset_request(
    user_data: PasswordReset,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):

    email = user_data.email

    user = await user_service.get_user_by_email(
        email,
        session
    )

    if not user:
        raise UserNotFound()

    token = create_url_safe_token({
        "email": email
    })

    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html = f"""
    <h1>Password Reset</h1>

    <p>Click the link below to reset your password:</p>

    <a href="{link}">Reset Password</a>
    """

    # Queue password reset email
    background_tasks.add_task(
    send_email_background,
    [email],
    "Reset Your Password",
    html
    )

    return JSONResponse(
        content={
            "message": "Password reset link sent to your email"
        },
        status_code=status.HTTP_200_OK
    )


# =====================================
# PASSWORD RESET CONFIRM
# =====================================

@auth_router.post("/password-reset-confirm/{token}")
async def password_reset_confirm(
    token: str,
    user_data: PasswordResetConfirm,
    session: AsyncSession = Depends(get_session),
):

    # Check password confirmation
    if user_data.new_password != user_data.confirm_password:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    # Decode reset token
    token_data = decode_url_self_token(token)

    if not token_data:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token"
        )

    email = token_data.get("email")

    if not email:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

    # Get user
    user = await user_service.get_user_by_email(
        email,
        session
    )

    if not user:
        raise UserNotFound()

    # Hash new password
    user.password_hash = generate_pass_hash(
        user_data.new_password
    )

    # Update database
    session.add(user)

    await session.commit()

    await session.refresh(user)

    return JSONResponse(
        content={
            "message": "Password reset successfully"
        },
        status_code=status.HTTP_200_OK
    )