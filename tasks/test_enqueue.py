import asyncio
import string

from core.app_queue import push_message, close_redis_connection
from core.config import settings


async def enqueue_letters_a_to_z():
    tasks = []
    for i in string.ascii_lowercase:
        print("enqueued", i)
        task = asyncio.create_task(push_message(settings.REDIS_QUEUE_NAME, i))
        tasks.append(task)
        
    results = await asyncio.gather(*tasks)
    await close_redis_connection()
    return results


def test_enqueue():
    result = asyncio.run(enqueue_letters_a_to_z())
    print(result)

if __name__ == "__main__":
    test_enqueue()