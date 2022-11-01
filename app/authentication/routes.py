from .schemas import Token, UserInDB
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from .security import (
    authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, 
    create_access_token, get_current_user, get_password_hash
)
from datetime import timedelta
from .schemas import User, CreateUser
from motor.motor_asyncio import AsyncIOMotorDatabase
from core.dependecies import get_db
import re

router = APIRouter(tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    print(type(db))
    user = await authenticate_user(
        form_data.username, form_data.password, db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/users", response_model=UserInDB)
async def register_user(
    user: CreateUser, db: AsyncIOMotorDatabase = Depends(get_db)
):

    print(user)

    if user.password1 != user.password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords must be the same",
        )

    regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
    pat = re.compile(regex)

    if not re.search(pat, user.password1):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invaid password",
        )

    user_dict = user.dict()
    user_dict['hashed_password'] = await get_password_hash(user.password1)
    del user_dict["password1"]
    del user_dict["password2"]

    print(user_dict)

    new_user = await db.users.insert_one(user_dict)
    print(new_user)
    saved_user = await db.users.find_one({"_id": new_user.inserted_id})
    print(saved_user)
    return saved_user
