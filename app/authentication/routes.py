from bson.objectid import ObjectId
from fastapi import APIRouter, Response, status, Depends, HTTPException
from app.authentication.oauth2 import AuthJWT
from fastapi_jwt_auth.exceptions import MissingTokenError
from app.core.database import user_collection
from app.authentication.schemas import (
    CreateUser, UserResponseSchema, LoginUser
)
from app.authentication.security import (
    hash_password, verify_password, set_access_token_cookie, 
    set_logged_in_cookie, set_refresh_token_cookie, generate_access_token,
    generate_refresh_token
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", 
    status_code=status.HTTP_201_CREATED, 
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
    user_exists = await user_collection.find_one(
        {"email": user_data.email.lower()}
    )

    if not user_exists:
        raise credentials_exception

    if not await verify_password(user_data.password, user_exists["password"]):
        raise credentials_exception

    access_token = await generate_access_token(user_exists, authorize)
    refresh_token = await generate_refresh_token(user_exists, authorize)

    await set_access_token_cookie(response, access_token)
    await set_refresh_token_cookie(response, refresh_token)
    await set_logged_in_cookie(response)

    return {'access_token': access_token, 'refresh_token': refresh_token}


@router.get('/refresh')
async def refresh_token(response: Response, authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_refresh_token_required()
        user_id = authorize.get_jwt_subject()

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not refresh access token'
            )

        user = await user_collection.find_one({'_id': ObjectId(str(user_id))})

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='The user belonging to this token no logger exist'
            )

        access_token = await generate_access_token(user, authorize)

    except MissingTokenError:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Please provide refresh token'
            )

    await set_access_token_cookie(response, access_token)
    await set_logged_in_cookie(response)

    return {'access_token': access_token}
