from pydantic import BaseModel, Field, EmailStr
from app.core.utils import PyObjectId
from bson import ObjectId


class User(BaseModel):
    username: str | None = None
    email: EmailStr

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "Jane Doe",
                "email": "jdoe@example.com",
            }
        }


class UserResponseSchema(User):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        

class CreateUser(User):
    username: str
    password: str
    confirm_password: str

    class Config:
        schema_extra = {
            "example": {
                "username": "Jane Doe",
                "email": "jdoe@example.com",
                "password": "Password1234*",
                "confirm_password": "Password1234*",
            }
        }


class LoginUser(User):
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "jdoe@example.com",
                "password": "Password1234*",
            }
        }
