from datetime import datetime, timedelta
from bson.objectid import ObjectId
from fastapi import APIRouter, Response, status, Depends, HTTPException
from app.authentication.oauth2 import AuthJWT
from app.core.database import user_collection
from app.core.config import settings
from app.authentication.schemas import CreateUser, UserResponseSchema
from app.authentication.security import hash_password

router = APIRouter(prefix="/auth", tags=["auth"])
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN


@router.post(
    "/register", status_code=status.HTTP_201_CREATED, 
    response_model=UserResponseSchema
)
async def register_user(user: CreateUser):
    user_exists = await user_collection.find_one({"email": user.email.lower()})

    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Account already exist'
        )

    if user.password != user.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Passwords do not match'
        )

    user.password = await hash_password(user.password)
    user.email = user.email.lower()
    saved_user = await user_collection.insert_one(
        user.dict(exclude={'confirm_password'})
    )
    user_from_db = await user_collection.find_one(
        {'_id': saved_user.inserted_id}
    )
    return user_from_db
