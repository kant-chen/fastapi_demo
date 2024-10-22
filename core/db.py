
import sqlalchemy.engine.url
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from core.config import settings
from core.models import Base


logger = settings.APP_LOGGER
SQLALCHEMY_DATABASE_URI = sqlalchemy.engine.url.URL.create(
    drivername="postgresql+asyncpg",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    database=settings.POSTGRES_DB,
)
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URI, echo=True, pool_size=100, max_overflow=20
)



def async_session_generator():
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db_session():
    try:
        async_session = async_session_generator()

        async with async_session() as session:
            logger.debug("DB session entered")
            yield session
    except:
        await session.rollback()
        logger.debug("DB session rolled back")
        raise
    finally:
        await session.close()
        logger.debug("DB session closed")


async def initialize_db():
    """ Import all modules that use `Base`"""
    from tasks import models as task_models # noqa
    logger.info("initialize_db")
    async with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            logger.info(f"creating table: {table.name}")
            await conn.run_sync(table.create, checkfirst=True)