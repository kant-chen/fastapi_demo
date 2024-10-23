import asyncio
import asyncio.subprocess
from signal import SIGINT
import subprocess

import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from worker import main as worker_main, shutdown_gracefully
from core.db import get_db_session
from tasks.query import get_task_by_id


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

    assert response_data["status"] == "pending"


@pytest.mark.anyio
async def test_cancel_task(http_client):
    message_text = "TestMessage"
    payload = {"message": message_text}
    response = await http_client.post("/tasks", json=payload)
    assert response.status_code == 200
    response_data = response.json()
    task_id = response_data["id"]
    payload = {"status": "canceled"}
    response = await http_client.patch(f"/tasks/{task_id}", json=payload)
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"] == "canceled"


@pytest.mark.anyio
async def test_task_consume(http_client):
    ids = []
    for i in range(1, 10):
        payload = {"message": str(i)}
        response = await http_client.post("/tasks", json=payload)
        assert response.status_code == 200
        ids.append(response.json()["id"])
    
    db_generator = get_db_session()
    db_session = await anext(db_generator)
    for task_id in ids:
        task_obj = await get_task_by_id(db_session, task_id)
        assert task_obj.status == "pending"

    # Run a shell command
    result = subprocess.Popen(["python", "worker.py"])
    await asyncio.sleep(5)
    result.send_signal(SIGINT)
    await asyncio.sleep(5)
    for task_id in ids:
        task_obj = await get_task_by_id(db_session, task_id)
        assert task_obj.status == "completed"

    

    

    