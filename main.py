from typing import Union

from fastapi import FastAPI
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, Request
from starlette.background import BackgroundTasks

from core.db import get_db_session, initialize_db
from core.config import settings
from tasks.schemas import TaskSchema, EnqueueRequest
from tasks.query import create_message_task

app = FastAPI()
logger = settings.APP_LOGGER



@app.post("/tasks", response_model=TaskSchema)
async def enqueue_message(
    request: Request,
    request_data: EnqueueRequest,
    db_session: AsyncSession = Depends(get_db_session)
) -> TaskSchema:
    message_to_put = request_data.message
    message = await create_message_task(db_session, message_to_put)
    await db_session.commit()

    response_obj = TaskSchema.model_validate(message)
    return response_obj


@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: int, q: Union[str, None] = None):
    return {"item_id": task_id, "q": q}


@app.on_event("startup")
async def startup_event():
    background_tasks = BackgroundTasks()
    background_tasks.add_task(initialize_db)
    await background_tasks()