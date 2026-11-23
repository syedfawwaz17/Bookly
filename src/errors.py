from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from typing import Any, Callable


# =====================================
# BASE EXCEPTION
# =====================================

class BooklyException(Exception):
    pass


# =====================================
# CUSTOM EXCEPTIONS
# =====================================

class InvalidToken(BooklyException):
    pass


class RevokedToken(BooklyException):
    pass


class AccessTokenRequired(BooklyException):
    pass


class RefreshTokenRequired(BooklyException):
    pass


class InvalidCredentials(BooklyException):
    pass


class UserAlreadyExists(BooklyException):
    pass


class InsufficientPermission(BooklyException):
    pass


class BookNotFound(BooklyException):
    pass


class TagNotFound(BooklyException):
    pass


class UserNotFound(BooklyException):
    pass


class TagAlreadyExists(BooklyException):
    pass
class AccountNotVerified(BooklyException):
    pass

# =====================================
# EXCEPTION HANDLER FACTORY
# =====================================

def create_exception_handler(
    status_code: int,
    initial_detail: Any
) -> Callable:

    async def exception_handler(
        request: Request,
        exc: BooklyException
    ):

        return JSONResponse(
            content=initial_detail,
            status_code=status_code
        )

    return exception_handler


# =====================================
# REGISTER ALL ERRORS
# =====================================

def register_all_errors(app: FastAPI):

    # BOOK NOT FOUND
    app.add_exception_handler(
        BookNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Book not found",
                "error_code": "book_not_found"
            }
        )
    )

    # INVALID CREDENTIALS
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_400_BAD_REQUEST,
            initial_detail={
                "message": "Invalid Email Or Password",
                "error_code": "invalid_email_or_password"
            }
        )
    )
    
    app.add_exception_handler(
        AccountNotVerified,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message":"Account is not verified",
                "resolution":"please check your email for verification",
                "error_code" : "not_verified"
            }
        )
    )

    # INVALID TOKEN
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or expired",
                "resolution": "Please get a new token",
                "error_code": "invalid_token"
            }
        )
    )

    # REVOKED TOKEN
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token has been revoked",
                "error_code": "revoked_token"
            }
        )
    )

    # ACCESS TOKEN REQUIRED
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Access token required",
                "error_code": "access_token_required"
            }
        )
    )

    # REFRESH TOKEN REQUIRED
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Refresh token required",
                "error_code": "refresh_token_required"
            }
        )
    )

    # USER ALREADY EXISTS
    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists"
            }
        )
    )

    # USER NOT FOUND
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found",
                "error_code": "user_not_found"
            }
        )
    )

    # INSUFFICIENT PERMISSION
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Insufficient permissions",
                "error_code": "insufficient_permission"
            }
        )
    )

    # TAG NOT FOUND
    app.add_exception_handler(
        TagNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "Tag not found",
                "error_code": "tag_not_found"
            }
        )
    )

    # TAG ALREADY EXISTS
    app.add_exception_handler(
        TagAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "Tag already exists",
                "error_code": "tag_already_exists"
            }
        )
    )