import inspect
import re

from beanie import Document, PydanticObjectId
from bson import ObjectId
from fastapi import HTTPException, status
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


def custom_openapi(app):
    def inner():
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title="Custom title",
            version="2.5.0",
            description="This is a very custom OpenAPI schema",
            routes=app.routes,
        )

        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }

        cookie_security_schemes = {
            "AuthJWTCookieAccess": {
                "type": "apiKey",
                "in": "header",
                "name": "X-CSRF-TOKEN"
            },
            "AuthJWTCookieRefresh": {
                "type": "apiKey",
                "in": "header",
                "name": "X-CSRF-TOKEN"
            }
        }

        refresh_token_cookie = {
            "name": "refresh_token_cookie",
            "in": "cookie",
            "required": False,
            "schema": {
                "title": "refresh_token_cookie",
                "type": "string"
            }
        }

        access_token_cookie = {
            "name": "access_token_cookie",
            "in": "cookie",
            "required": False,
            "schema": {
                "title": "access_token_cookie",
                "type": "string"
            }
        }

        if "components" in openapi_schema:
            openapi_schema["components"].update(
                {"securitySchemes": cookie_security_schemes}
            )
        else:
            openapi_schema["components"] = {
                "securitySchemes": cookie_security_schemes
            }

        api_router = [
            route for route in app.routes if isinstance(route, APIRoute)
        ]

        for route in api_router:
            path = getattr(route, "path")
            endpoint = getattr(route, "endpoint")
            methods = [method.lower() for method in getattr(route, "methods")]

            for method in methods:
                if (
                    re.search(
                        "jwt_required", inspect.getsource(endpoint)
                    ) or re.search(
                        "fresh_jwt_required", inspect.getsource(endpoint)
                    ) or re.search(
                        "jwt_optional", inspect.getsource(endpoint)
                    )
                ):
                    try:
                        params = openapi_schema["paths"][path][method][
                            'parameters'
                        ]
                        params.append(access_token_cookie)
                    except KeyError:
                        openapi_schema["paths"][path][method].update(
                            {"parameters": [access_token_cookie]}
                        )

                    if method != "get":
                        openapi_schema["paths"][path][method].update({
                            'security': [{"AuthJWTCookieAccess": []}]
                        })

                if re.search(
                    "jwt_refresh_token_required", inspect.getsource(endpoint)
                ):
                    try:
                        params = openapi_schema["paths"][path][method][
                            'parameters'
                        ]
                        params.append(refresh_token_cookie)
                    except KeyError:
                        openapi_schema["paths"][path][method].update(
                            {"parameters": [refresh_token_cookie]}
                        )

                    if method != "get":
                        openapi_schema["paths"][path][method].update({
                            'security': [{"AuthJWTCookieRefresh": []}]
                        })

        app.openapi_schema = openapi_schema
        return app.openapi_schema
    return inner


async def get_or_404(model: Document, id: PydanticObjectId) -> Document:
    instance = await model.get(id)

    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Such birthday does not exist'
        )

    return instance
