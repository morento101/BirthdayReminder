from pydantic import BaseModel, Field, EmailStr
from core.utils import PyObjectId
from bson import ObjectId


class User(BaseModel):
    username: str
    email: EmailStr

    class Config:
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
    password: str
    confirm_password: str

    class Config:
        schema_extra = BaseModel.Config.schema_extra + {
            "password": "Password1234*",
            "confirm_password": "Password1234*",
        }
 