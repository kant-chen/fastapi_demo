from uuid import uuid4

from sqlalchemy.ext.asyncio.session import AsyncSession

from tasks.models import Task

async def create_message_task(db_session: AsyncSession, message_to_put: str) -> Task:
    _uuid = str(uuid4())
    task = Task(id=_uuid, message=message_to_put, status="pending")
    db_session.add(task)
    return task