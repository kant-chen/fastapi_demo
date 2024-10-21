import asyncio
import string

from core.app_queue import push_message
from core.config import settings


async def enqueue_letters_a_to_z():
    tasks = []
    for i in string.ascii_lowercase:
        print("enqueued", i)
        task = asyncio.create_task(push_message(settings.REDIS_QUEUE_NAME, i))
        tasks.append(task)
        
    results = await asyncio.gather(*tasks)   
    return results


def test_enqueue():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(enqueue_letters_a_to_z())
    print(result)

if __name__ == "__main__":
    test_enqueue()