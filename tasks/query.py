from uuid import uuid4
from typing import Optional

from sqlalchemy.ext.asyncio.session import AsyncSession
import sqlalchemy.exc
from sqlalchemy import select

from tasks.models import Task

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
