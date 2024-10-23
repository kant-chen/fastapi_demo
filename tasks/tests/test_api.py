import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


BASE_URL = "http://127.0.0.1:8000" 


@pytest.fixture(scope="module")
async def http_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=BASE_URL
    ) as async_http_client:
        yield async_http_client


@pytest.mark.anyio
async def test_create_task(http_client):
    message_text = "TestMessage"
    payload = {"message": message_text}
    response = await http_client.post("/tasks", json=payload)
    assert response.status_code == 200
    response_data = response.json()
    for field in ["id", "message", "status"]:
        assert field in response_data