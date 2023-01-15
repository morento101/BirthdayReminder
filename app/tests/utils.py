from app.main import app


async def register_test_user(client_test, register_user_data):
    return await client_test.post(
        app.url_path_for('register_user'), json=register_user_data
    )


async def login_test_user(client_test, login_data):
    return await client_test.post(app.url_path_for('login'), json=login_data)


async def setup_test_user(client_test, register_user_data, login_data):
    user_response = await register_test_user(client_test, register_user_data)
    await login_test_user(client_test, login_data)

    return user_response


async def add_test_birthday(client_test, birthday_data):
    return await client_test.post(
        app.url_path_for('add_birthday'), json=birthday_data
    )
