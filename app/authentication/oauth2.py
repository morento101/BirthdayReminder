import base64
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from app.core.config import settings
from fastapi import Depends, HTTPException, status
from bson import ObjectId
from fastapi_jwt_auth.exceptions import MissingTokenError
from app.database.models import UserModel


class AuthSettings(BaseModel):
    authjwt_secret_key: str = settings.SECRET_KEY
    authjwt_algorithm: str = settings.JWT_ALGORITHM
    authjwt_decode_algorithms: list[str] = [settings.JWT_ALGORITHM]
    authjwt_token_location: set = {'cookies', 'headers'}

    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_secure: bool = False
    authjwt_cookie_csrf_protect: bool = True
    # Change to 'lax' in production to make your website more secure from CSRF Attacks, default is None # noqa
    # authjwt_cookie_samesite: str = 'lax'

    authjwt_public_key: str = base64.b64decode(
        settings.JWT_PUBLIC_KEY
    ).decode('utf-8')

    authjwt_private_key: str = base64.b64decode(
        settings.JWT_PRIVATE_KEY
    ).decode('utf-8')


@AuthJWT.load_config
def get_config():
    return AuthSettings()


async def get_current_user(authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
        user_id = authorize.get_jwt_subject()

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not refresh access token'
            )

        user = await UserModel.get(ObjectId(str(user_id)))

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='User does not exist'
            )

    except MissingTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You are not logged in'
        )

    return user
