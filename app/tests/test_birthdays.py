import pytest

from app.main import app
from app.tests.fixtures import login_data, register_user_data, birthday_data
from app.tests.utils import setup_test_user, add_test_birthday
from app.database.models import BirthdayModel


@pytest.mark.anyio
async def test_create_birthday(
    client_test,
    register_user_data,
    login_data,
    birthday_data: dict
):
    await setup_test_user(client_test, register_user_data, login_data)

    response = await add_test_birthday(client_test, birthday_data)
    assert response.status_code == 201

    response_data = response.json()
    birthday_data.update({"_id": None})
    keys = birthday_data.keys()
    for key in keys:
        assert key in response_data


@pytest.mark.anyio
async def test_get_birthday(
    client_test,
    register_user_data,
    login_data,
    birthday_data: dict
):
    await setup_test_user(client_test, register_user_data, login_data)

    birthday = await add_test_birthday(client_test, birthday_data)
    birthday_id = birthday.json()["_id"]

    response = await client_test.get(
        app.url_path_for('get_birthday', birthday_id=birthday_id)
    )
    assert response.status_code == 200

    response_data = response.json()
    birthday_data.update({"_id": None})
    keys = birthday_data.keys()
    for key in keys:
        assert key in response_data


@pytest.mark.anyio
async def test_edit_birthday(
    client_test,
    register_user_data,
    login_data,
    birthday_data
):
    await setup_test_user(client_test, register_user_data, login_data)

    birthday = await add_test_birthday(client_test, birthday_data)
    birthday_id = birthday.json()["_id"]

    get_birthday = await client_test.get(
        app.url_path_for('get_birthday', birthday_id=birthday_id)
    )
    get_birthday_data = get_birthday.json()

    edit_birthday_response = await client_test.patch(
        app.url_path_for('get_birthday', birthday_id=birthday_id),
        json={"title": "changed"}
    )
    edit_birthday_data = edit_birthday_response.json()

    assert edit_birthday_response.status_code == 200
    assert get_birthday_data["title"] != edit_birthday_data["title"]


@pytest.mark.anyio
async def test_edit_birthday(
    client_test,
    register_user_data,
    login_data,
    birthday_data
):
    await setup_test_user(client_test, register_user_data, login_data)

    birthday = await add_test_birthday(client_test, birthday_data)
    birthday_id = birthday.json()["_id"]

    delete_response = await client_test.delete(
        app.url_path_for('delete_birthday', birthday_id=birthday_id)
    )
    assert delete_response.status_code == 204
