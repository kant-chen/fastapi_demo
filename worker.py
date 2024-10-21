import asyncio
from asyncio.queues import Queue
from signal import SIGINT, SIGTERM

from core.app_queue import consume_message, conn
from core.config import settings

logger = settings.APP_LOGGER
worker_queue = Queue(maxsize=settings.WORKER_QUEUE_MAXSIZE)
concuruent_task_count = 0
shut_off_program = False



async def execute_task(msg):
    global concuruent_task_count
    is_done = False
    try:
        logger.info(f"started execution: {msg} , concuruent_task_count={concuruent_task_count}")
        # TODO: Update task record in DB, status = processing
        await asyncio.sleep(3)
        # TODO: Update task record in DB, status = completed
        is_done = True
    finally:
        concuruent_task_count -= 1
        logger.info(f"ended execution: {msg}, concuruent_task_count={concuruent_task_count} is_done={is_done}")



async def pull_messages_from_redis(shutdown_event: asyncio.Event):
    global concuruent_task_count
    while shut_off_program is False:
        logger.info("pull_messages_from_redis")
        if worker_queue.qsize() + concuruent_task_count < settings.WORKER_QUEUE_MAXSIZE:
            message = await consume_message(settings.REDIS_QUEUE_NAME, 1)
            if message:
                await worker_queue.put(message)
            else:
                await asyncio.sleep(1)
        else:
            await asyncio.sleep(1)

    logger.info("stopping coroutine: pull_messages_from_redis")
    shutdown_event.set()

async def schedule_task_to_worker(shutdown_event: asyncio.Event):
    global concuruent_task_count
    while shut_off_program is False:
        logger.info(f"schedule_task_to_worker, shut_off_program={shut_off_program}")
        tasks = []
        while worker_queue.empty() is False:
            message = await worker_queue.get()
            task = asyncio.create_task(execute_task(message))
            tasks.append(task)
        if len(tasks) > 0:
            concuruent_task_count += len(tasks)
            asyncio.gather(*tasks)

        await asyncio.sleep(1)  # Give up control to trigger tasks to run

    logger.info("stopping coroutine: schedule_task_to_worker")
    shutdown_event.set()


async def start_worker():
    event_pull_message = asyncio.Event()
    event_schduler = asyncio.Event()
    try:
        task_message_receiver = asyncio.create_task(pull_messages_from_redis(event_pull_message))
        task_scheduler = asyncio.create_task(schedule_task_to_worker(event_schduler))
        await asyncio.gather(task_message_receiver, task_scheduler)
    finally:
        logger.info("Gracefully shuttig down")
        global shut_off_program
        shut_off_program = True
        await asyncio.sleep(2)
        logger.info("closing redis connection")
        await conn.aclose()
        logger.info("waiting for task schedulers to complete")
        await event_pull_message.wait()
        await event_schduler.wait()
        logger.info(f"exitting start_worker")


def shutdown_gracefully():
    global shut_off_program
    shut_off_program = True
    logger.info("shutdown_gracefully() is called")


async def main():
    task = asyncio.create_task(start_worker())
    loop = asyncio.get_event_loop()
    for signal in [SIGINT, SIGTERM]:
        loop.add_signal_handler(signal, shutdown_gracefully)
    await task
    await asyncio.gather(*asyncio.all_tasks() - {asyncio.current_task()})

if __name__ == "__main__":
    asyncio.run(main())
        