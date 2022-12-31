from asgiref.sync import async_to_sync

from datetime import date

from app.core.config import initiate_database, settings
from app.database.models import BirthdayModel


@async_to_sync
async def get_all_today_birthdays() -> list[BirthdayModel]:
    today_date = date.today()
    await initiate_database()
    return await BirthdayModel.find(
        {"day": today_date.day, "month": today_date.month}
    ).to_list()
