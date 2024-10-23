from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import APIRouter, Depends, Request
from starlette.background import BackgroundTasks

from core.db import get_db_session, initialize_db
from core.app_queue import push_message
from core.config import settings
from tasks.schemas import TaskSchema, TaskCreateSchema, TaskUpdateSchema
from tasks.query import create_message_task, update_status_in_db
from tasks.exceptions import TaskNotfound, TaskStatusUpdateNotAllowed

app = FastAPI()
logger = settings.APP_LOGGER



@app.post("/tasks", response_model=TaskSchema)
async def enqueue_message(
    request: Request,
    request_data: TaskCreateSchema,
    background_tasks: BackgroundTasks,
    db_session: AsyncSession = Depends(get_db_session)
) -> TaskSchema:
    message_to_put = request_data.message
    message = await create_message_task(db_session, message_to_put)
    await db_session.commit()

    background_tasks.add_task(push_message, settings.REDIS_QUEUE_NAME, message.id)
    response_obj = TaskSchema.model_validate(message)
    return response_obj


@app.patch("/tasks/{task_id}", response_model=TaskSchema)
async def update_task(
    request: Request,
    task_id: str,
    request_data: TaskUpdateSchema,
    db_session: AsyncSession = Depends(get_db_session),

) -> TaskSchema:
    try:
        task_in_db = await update_status_in_db(db_session, task_id, request_data.status)
    except TaskNotfound:
        raise HTTPException(status_code=404, detail="Item not found")
    
    except TaskStatusUpdateNotAllowed:
        raise HTTPException(status_code=400, detail="Cancel is not allowed")


    response_obj = TaskSchema.model_validate(task_in_db)
    await db_session.commit()
    return response_obj


@app.on_event("startup")
async def startup_event():
    background_tasks = BackgroundTasks()
    background_tasks.add_task(initialize_db)
    await background_tasks()