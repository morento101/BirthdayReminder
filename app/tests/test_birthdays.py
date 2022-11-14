from app.main import app
import pytest
from app.tests.fixtures import register_user_data, login_data


@pytest.fixture
async def birthday_data():
    return {
        "title": "Test Birthday",
        "description": "Tesc Description",
        "day": 5,
        "month": 1,
        "notification_time": "10:10:10"
    }


@pytest.mark.anyio
async def create_birthday(client_test, birthday_data: dict):
    await client_test.post(
        app.url_path_for('register_user'), json=register_user_data
    )
    await client_test.post(app.url_path_for('login'), json=login_data)
    response = await client_test.post(
        app.url_path_for('add_birthday'), json=birthday_data
    )

    assert response.status_code == 201

    response_data = response.json()
    keys = birthday_data.keys().update({"_id"})
    for key in keys:
        assert key in response_data


@pytest.mark.anyio
async def get_birthday(client_test, birthday_data: dict):
    await client_test.post(
        app.url_path_for('register_user'), json=register_user_data
    )
    await client_test.post(app.url_path_for('login'), json=login_data)
    birthday_id = await client_test.post(
        app.url_path_for('add_birthday'), json=birthday_data
    ).json()["_id"]

    response = await client_test.get(
        app.url_path_for('get_birthday', birthday_id=birthday_id)
    )

    assert response.status_code == 200
    assert response.json() == birthday_data
