from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from datetime import timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def hash_password(password):
    return pwd_context.hash(password)


async def generate_access_token(user, authorize):
    return authorize.create_access_token(
        subject=str(user.id),
        expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
    )


async def generate_refresh_token(user, authorize):
    return authorize.create_refresh_token(
        subject=str(user.id),
        expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN)
    )


async def set_access_token_cookie(response, access_token):
    response.set_cookie(
        'access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60, httponly=True,
    )


async def set_refresh_token_cookie(response, refresh_token):
    response.set_cookie(
        'refresh_token', refresh_token, REFRESH_TOKEN_EXPIRES_IN * 60,
        REFRESH_TOKEN_EXPIRES_IN * 60, httponly=True,
    )


async def set_logged_in_cookie(response):
    response.set_cookie(
        'logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60, 
        ACCESS_TOKEN_EXPIRES_IN * 60,
    )
