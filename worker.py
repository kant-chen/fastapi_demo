import asyncio
from asyncio.queues import Queue

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

    shutdown_event.set()

async def schedule_task_to_worker(shutdown_event: asyncio.Event):
    global concuruent_task_count
    while shut_off_program is False:
        logger.info("schedule_task_to_worker")
        tasks = []
        while worker_queue.empty() is False:
            message = await worker_queue.get()
            task = asyncio.create_task(execute_task(message))
            tasks.append(task)
        if len(tasks) > 0:
            concuruent_task_count += len(tasks)
            asyncio.gather(*tasks)

        await asyncio.sleep(1)  # Give up control to trigger tasks to run

    shutdown_event.set()



async def start_worker():
    event_pull_message = asyncio.Event()
    event_schduler = asyncio.Event()
    try:
        task_message_receiver = asyncio.create_task(pull_messages_from_redis(event_pull_message))
        task_scheduler = asyncio.create_task(schedule_task_to_worker(event_schduler))
        await asyncio.gather(task_message_receiver, task_scheduler)
    except asyncio.CancelledError:
        logger.info("Gracefully shuttig down")
        # TODO: When CancelledError is raised, stop task_message_receiver and task_scheduler
        #   and wait for all existing tasks to finish
        global shut_off_program
        shut_off_program = True
        await event_pull_message.wait()
        await event_schduler.wait()
        # wait again to let them exit from while loop
        # await asyncio.gather(task_message_receiver, task_scheduler)
        # wait for all scheduled tasks to complete
        conn.close()
        all_tasks_except_current = asyncio.all_tasks().difference(asyncio.current_task())
        await asyncio.gather(*all_tasks_except_current)
    
async def main():
    task = asyncio.create_task(start_worker())
    try:
        await task
    except KeyboardInterrupt:
        # Trigger start_worker to raise CancelledError
        task.cancel()

if __name__ == "__main__":
    # try:
    asyncio.run(main())
    # except KeyboardInterrupt:
    #     # exit(0)
        