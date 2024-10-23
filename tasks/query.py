from uuid import uuid4
from typing import Optional, Literal

from sqlalchemy.ext.asyncio.session import AsyncSession
import sqlalchemy.exc
from sqlalchemy import select

from core.config import settings
from tasks.models import Task
from tasks.exceptions import TaskNotfound, TaskStatusUpdateNotAllowed

logger = settings.APP_LOGGER

async def create_message_task(db_session: AsyncSession, message_to_put: str) -> Task:
    _uuid = str(uuid4())
    task = Task(id=_uuid, message=message_to_put, status="pending")
    db_session.add(task)
    return task


async def get_task_by_id(db_session: AsyncSession, task_id: str) -> Optional[Task]:
    try:
        q = select(Task).filter_by(id=task_id)
        result = await db_session.execute(q)
        return result.one()[0]
    except sqlalchemy.exc.NoResultFound:
        return None


async def update_status_in_db(
    db_session: AsyncSession,
    task_id_in_db: str,
    target_status: Literal["processing", "completed", "canceled"],
) -> Task:
    """
    Update status="processing"
    """
    task_db_obj = await get_task_by_id(db_session, task_id_in_db)
    if task_db_obj is None:
        logger.error(f"task_id: {task_id_in_db} not found in the DB")
        raise TaskNotfound

    current_status = task_db_obj.status
    if target_status not in ["processing", "completed", "canceled"]:
        raise ValueError(f"target_status: {target_status} not allowed")
    elif target_status in ["canceled", "processing"] and current_status != "pending":
        raise TaskStatusUpdateNotAllowed
    elif target_status == "completed" and current_status != "processing":
        raise TaskStatusUpdateNotAllowed

    task_db_obj.status = target_status
    return task_db_obj