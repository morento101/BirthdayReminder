from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.authentication.oauth2 import AuthJWT, get_current_user
from app.authentication.schemas import (CreateUser, LoginUser,
                                        UserResponseSchema)
from app.authentication.security import (generate_access_token,
                                         generate_refresh_token, hash_password,
                                         set_access_token_cookie,
                                         set_logged_in_cookie,
                                         set_refresh_token_cookie,
                                         verify_password)
from app.database.models import UserModel


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: CreateUser):
    user_exists = await UserModel.find(
        UserModel.email == user.email.lower()
    ).first_or_none()

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
    saved_user = await UserModel(
        **user.dict(exclude={'confirm_password'})
    ).create()
    user_from_db = await UserModel.get(saved_user.id)
    return user_from_db.dict(exclude={"password"})


@router.post('/login')
async def login(
    user_data: LoginUser,
    response: Response,
    authorize: AuthJWT = Depends()
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Incorrect Email or Password'
    )
    user_exists = await UserModel.find_one({"email": user_data.email.lower()})

    if not user_exists:
        raise credentials_exception

    if not await verify_password(user_data.password, user_exists.password):
        raise credentials_exception

    access_token = await generate_access_token(user_exists, authorize)
    refresh_token = await generate_refresh_token(user_exists, authorize)

    await set_access_token_cookie(response, access_token)
    await set_refresh_token_cookie(response, refresh_token)
    await set_logged_in_cookie(response)

    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.get('/refresh')
async def refresh_token(
    response: Response,
    authorize: AuthJWT = Depends(),
    user: dict = Depends(get_current_user)
):
    access_token = await generate_access_token(user, authorize)
    await set_access_token_cookie(response, access_token)
    await set_logged_in_cookie(response)
    return {'access_token': access_token}


@router.get('/logout', status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    authorize: AuthJWT = Depends(),
    user: dict = Depends(get_current_user)
):
    authorize.unset_jwt_cookies()
    response.set_cookie('logged_in', '', -1)
    return {'status': 'success'}


@router.get('/me', response_model=UserResponseSchema)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponseSchema(**user.dict())
