import pytest
from httpx import AsyncClient

from app.core.config import initiate_database
from app.main import app


@pytest.fixture()
async def client_test():
    await initiate_database(database="test", mode="test")

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def anyio_backend():
    return 'asyncio'
