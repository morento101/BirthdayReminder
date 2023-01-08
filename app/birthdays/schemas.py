from pydantic import BaseModel, validator
from datetime import time


class Birthday(BaseModel):
    title: str
    name_of_birthday_boy: str
    description: str | None = None
    day: int
    month: int
    notification_time: time

    @validator('day')
    def day_range(cls, value):
        if value not in range(1, 32):
            raise ValueError('Day must be in range from 1 to 31')
        return value

    @validator('month')
    def month_range(cls, value):
        if value not in range(1, 13):
            raise ValueError('Month must be in range from 1 to 13')
        return value

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "title": "Yaroslav's Birthday",
                "name_of_birthday_boy": "Anton",
                "description": "Birthday of my friend from McDonalds",
                "day": 2,
                "month": 11,
                "notification_time": "15:30:00"
            }
        }


class UpdateBirthday(Birthday):
    title: str | None = None
    description: str | None = None
    day: str | None = None
    month: str | None = None
    notification_time: str | None = None
