
from sqlalchemy import Column, String
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ENUM

from core.models import Base


task_status_enum = ENUM(
    "pending", "canceled", "processing", "completed", name="task_status"
)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    message = Column(String, nullable=False)
    status = Column(task_status_enum, nullable=False, comment="Task status")

