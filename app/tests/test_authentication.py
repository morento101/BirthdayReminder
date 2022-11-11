from app.main import app
import pytest
from app.tests.fixtures import register_user_data, login_data


@pytest.mark.anyio
async def test_root(client_test):
    response = await client_test.get(app.url_path_for("home"))

    assert response.status_code == 200
    assert response.json() == {"data": "Home Page"}


@pytest.mark.anyio
async def test_register_user(client_test, register_user_data):
    response = await client_test.post(
        app.url_path_for('register_user'), json=register_user_data
    )

    assert response.status_code == 201

    response_data = response.json()
    assert register_user_data["username"] == response_data["username"]
    assert register_user_data["email"] == response_data["email"]
    assert "password" not in response_data
    assert "confirm_password" not in response_data


@pytest.mark.anyio
async def test_login(client_test, register_user_data, login_data):
    await client_test.post(
        app.url_path_for('register_user'), json=register_user_data
    )

    response = await client_test.post(
        app.url_path_for('login'), json=login_data
    )

    assert response.status_code == 200

    response_data = response.json()
    assert 'access_token' in response_data
    assert 'refresh_token' in response_data


@pytest.mark.anyio
async def test_refresh(client_test, register_user_data, login_data):
    await client_test.post(
        app.url_path_for('register_user'), json=register_user_data
    )

    login_response = await client_test.post(
        app.url_path_for('login'), json=login_data
    )
    login_response_data = login_response.json()

    refresh_response = await client_test.get(
        app.url_path_for('refresh_token')
    )
    assert refresh_response.status_code == 200

    refresh_response_data = refresh_response.json()
    old_access_token = login_response_data['access_token']
    new_access_token = refresh_response_data['access_token']
    assert old_access_token != new_access_token


@pytest.mark.anyio
async def test_logout(client_test, register_user_data, login_data):
    await client_test.post(
        app.url_path_for('register_user'), json=register_user_data
    )
    await client_test.post(app.url_path_for('login'), json=login_data)
    response = await client_test.get(app.url_path_for('logout'))

    assert response.status_code == 200
    assert 'access_token' not in response.cookies
    assert 'refresh_token' not in response.cookies
    assert 'logged_in' not in response.cookies


@pytest.mark.anyio
async def test_get_me_url(client_test, register_user_data, login_data):
    await client_test.post(
        app.url_path_for('register_user'), json=register_user_data
    )
    await client_test.post(app.url_path_for('login'), json=login_data)
    response = await client_test.get(app.url_path_for('get_me'))

    assert response.status_code == 200

    response_data = response.json()
    assert '_id' in response_data
    assert register_user_data['email'] == response_data['email']
    assert register_user_data['username'] == response_data['username']
