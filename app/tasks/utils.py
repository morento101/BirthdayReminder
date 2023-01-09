from datetime import date

from asgiref.sync import async_to_sync

from app.core.config import initiate_database
from app.database.models import BirthdayModel, UserModel


@async_to_sync
async def get_all_today_birthdays() -> list[BirthdayModel]:
    today_date = date.today()
    await initiate_database()
    return await BirthdayModel.find(
        {"day": today_date.day, "month": today_date.month}
    ).to_list()


@async_to_sync
async def get_user_data_from_birthday(birthday: BirthdayModel):
    await initiate_database()
    return await UserModel.find_one(UserModel.birthdays.id == birthday.id)
