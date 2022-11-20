import pytest


@pytest.fixture()
async def register_user_data():
    return {
        "username": "test",
        "email": "test@example.com",
        "password": "SuperPassword1234*",
        "confirm_password": "SuperPassword1234*",
    }


@pytest.fixture()
async def login_data():
    return {
        "email": "test@example.com",
        "password": "SuperPassword1234*",
    }


@pytest.fixture()
async def birthday_data() -> dict:
    return {
        "title": "Test Birthday",
        "description": "Tesc Description",
        "day": 5,
        "month": 1,
        "notification_time": "10:10:10"
    }
