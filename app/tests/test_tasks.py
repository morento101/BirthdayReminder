from datetime import date

import pytest

from app.database.models import BirthdayModel, UserModel
from app.tasks.utils import (get_all_today_birthdays,
                             get_user_data_from_birthday)
from app.tests.fixtures import birthday_data, login_data, register_user_data
from app.tests.utils import add_test_birthday, setup_test_user


@pytest.mark.anyio
async def test_get_all_today_birthdays(
    client_test,
    register_user_data,
    login_data,
    birthday_data
):
    today_date = date.today()
    birthday_data.update({"day": today_date.day, "month": today_date.month})

    await setup_test_user(client_test, register_user_data, login_data)

    birthday_response = await add_test_birthday(client_test, birthday_data)
    birthday = await BirthdayModel.get(birthday_response.json()["_id"])

    assert birthday in await get_all_today_birthdays()


# motormock does not support dbref which is the core of relations in beanie
# so we need to skip test below
# waiting for the new version of library to fix this issue
@pytest.mark.skip
@pytest.mark.anyio
async def test_get_user_data_from_birthday(
    client_test,
    register_user_data,
    login_data,
    birthday_data
):
    today_date = date.today()
    birthday_data.update({"day": today_date.day, "month": today_date.month})

    user_response = await setup_test_user(
        client_test, register_user_data, login_data
    )

    birthday_response = await add_test_birthday(client_test, birthday_data)
    birthday = await BirthdayModel.get(birthday_response.json()["_id"])

    user = await UserModel.get(user_response.json()["id"], fetch_links=True)

    assert user == await get_user_data_from_birthday(birthday)
