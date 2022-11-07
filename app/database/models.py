from beanie import Document, Indexed
from pydantic import EmailStr


class User(Document):
    username: str | None = None
    email:  Indexed(EmailStr, unique=True)
    password: str

    class Settings:
        name = "users"
