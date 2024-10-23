import logging
import logging.config

from pydantic_settings import BaseSettings
from redis import Redis

from core.log_setting import log_setting

logging.config.dictConfig(log_setting)


class Settings(BaseSettings):
    # PostgreSQL
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "fastapi_demo"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_QUEUE_NAME: str = "fastapi-demo"

    APP_LOGGER: logging.Logger = logging.getLogger("api_server")
    WORKER_QUEUE_MAXSIZE: int = 100


settings = Settings()
