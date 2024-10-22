
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, text
from sqlalchemy.sql import func


class Base(AsyncAttrs, DeclarativeBase):
    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        server_default=text("NOW()::timestamp"),
    )

    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        server_default=text("NOW()::timestamp"),
        onupdate=func.now(),
    )