from pydantic import BaseModel, Field, ConfigDict
import datetime


class EnqueueRequest(BaseModel):
    message: str = Field(
        title="the message text",
        description="the message text",
        example="Hello"
    )


class TaskSchema(BaseModel):
    class Config:
        from_attributes = True

    id: str = Field(
        title="id",
        description="UUID of the message",
        example="2bbe0835-fc66-45e3-97ea-da7e8093d78a"
    )
    message: str = Field(
        title="message",
        description="message content",
        example="Hello"
    )
    status: str = Field(
        title="status",
        description="processing status",
        example="pending"
    )
    created_at: datetime.datetime = Field(
        title="created_at",
        description="creation time",
        example="2024-10-22 10:25:47.116777"
    )
    updated_at: datetime.datetime = Field(
        title="updated_at",
        description="update time",
        example="2024-10-22 10:25:47.116777"
    )


