from passlib.context import CryptContext
from datetime import datetime, timedelta
import uuid
import jwt
from src.config import Config
import logging
from itsdangerous import URLSafeTimedSerializer
password_context = CryptContext(
    schemes=["bcrypt"]
)

ACCESS_TOKEN_EXPIRY = 3600


def generate_pass_hash(password: str) -> str:
    return password_context.hash(password)


def verify_pass_hash(password: str, hash_pass: str) -> bool:
    return password_context.verify(password, hash_pass)


def create_access_token(
    user_data: dict,
    expiry: timedelta = None,
    refresh: bool = False,
):
    payload = {
        "user": user_data,
        "exp": datetime.utcnow()
        + (expiry if expiry else timedelta(seconds=ACCESS_TOKEN_EXPIRY)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh,
    }

    print("ENCODE SECRET:", repr(Config.JWT_SECRET))
    print("ENCODE ALGO:", repr(Config.JWT_ALGORITHM))

    token = jwt.encode(
        payload,
        Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM,
    )

    return token


def decode_token(token: str):
    try:
        print("TOKEN RECEIVED:", token)
        print("DECODE SECRET:", repr(Config.JWT_SECRET))
        print("DECODE ALGO:", repr(Config.JWT_ALGORITHM))

        payload = jwt.decode(
            token,
            Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM],
        )

        print("DECODED PAYLOAD:", payload)

        return payload

    except jwt.PyJWTError as e:
        logging.exception(e)
        return None
seralizer = URLSafeTimedSerializer(
        secret_key=Config.JWT_SECRET,
        salt="email-configuration"
    )  
def create_url_safe_token(data:dict):
   
    
    token = seralizer.dumps(data)
    return token
def decode_url_self_token(token: str):
    try:
        token_data = seralizer.loads(token)
        return token_data

    except Exception as e:
        logging.error(str(e))
        