from beanie import Document, Indexed, Link
from pydantic import EmailStr
from datetime import time


class BirthdayModel(Document):
    title: str
    name_of_birthday_boy: str
    description: str = ""
    day: int
    month: int
    notification_time: time

    class Settings:
        name = "birthdays"
        bson_encoders = {
            time: str
        }


class UserModel(Document):
    username: str | None = None
    email: Indexed(EmailStr, unique=True)
    password: str
    birthdays: list[Link[BirthdayModel]] | None = None

    class Settings:
        name = "users"
