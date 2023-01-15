from datetime import date

from app.database.models import BirthdayModel, UserModel


async def get_all_today_birthdays() -> list[BirthdayModel]:
    today_date = date.today()
    return await BirthdayModel.find(
        {"day": today_date.day, "month": today_date.month}
    ).to_list()


async def get_user_data_from_birthday(birthday: BirthdayModel):
    return await UserModel.find_one(UserModel.birthdays.id == birthday.id)
