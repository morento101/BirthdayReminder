from core import settings
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from .schemas import TokenData, UserInDB
from motor.motor_asyncio import AsyncIOMotorDatabase
from core.dependecies import get_db

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_password_hash(password):
    return pwd_context.hash(password)


async def create_access_token(
    data: dict, expires_delta: timedelta | None = None
):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


async def get_user(username: str, db: AsyncIOMotorDatabase):
    user = await db.users.find_one({ "username": username })

    if user is None:
        return

    user["hashed_password"] = user["password"]
    del user["password"]

    return UserInDB(**user)


async def authenticate_user(
    username: str, password: str, db: AsyncIOMotorDatabase
):
    user = await get_user(username, db)

    if user is None:
        return

    if await verify_password(password, user.hashed_password):
        return user


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    creadentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")

        if username is None:
            raise creadentials_exception

        token_data = TokenData(username=username)

    except JWTError:
        raise creadentials_exception

    user = await get_user(username=token_data.username, db=db)

    if user is None:
        raise creadentials_exception

    return user
