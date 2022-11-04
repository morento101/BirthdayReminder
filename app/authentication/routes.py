from datetime import datetime, timedelta
from bson.objectid import ObjectId
from fastapi import APIRouter, Response, status, Depends, HTTPException
from authentication.oauth2 import AuthJWT
from core.database import user_collection
from core.config import settings

router = APIRouter(prefix="/auth" tags=["auth"])
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN
