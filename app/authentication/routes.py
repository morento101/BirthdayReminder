from .schemas import Token
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .security import (
    authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, 
    create_access_token, get_current_user
)
from datetime import timedelta
from .schemas import User
from motor.motor_asyncio import AsyncIOMotorClient
from core.dependecies import get_client

router = APIRouter()

@router.post("/token", response_model=Token, tags=["auth"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    client: AsyncIOMotorClient = Depends(get_client)
):
    user = await authenticate_user(
        form_data.username, form_data.password, client
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


@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
