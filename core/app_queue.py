from redis.asyncio import Redis


from core.config import settings

conn = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
logger = settings.APP_LOGGER

async def push_message(queue_name: str, message: str):
    msg_cnt = await conn.lpush(queue_name, message)
    logger.info(f"Message: {message} has enqueued. ")
    logger.info(f"There are {msg_cnt} messages in the queue")
    return msg_cnt

async def consume_message(queue_name, timeout=0):
    result = await conn.brpop(queue_name, timeout=timeout)
    msg = None
    if result:
        _, msg = result
        msg = msg.decode()
    return msg