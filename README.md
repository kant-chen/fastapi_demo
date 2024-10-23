# FastAPI demo project
### Implement a high-throughput task processing app using Python FastAPI
This is a project that demonstrate how to use FastAPI to implment asynchronous APIs

## Architecture Overview
### Use micro-service architecture
There are 3 docker services defined in `docker-compose.yml`:
- db: PostgreSQL v16.4
- redis: Redis v7.4
- api-server: FastAPI

### FastAPI Service
There are 2 entrypoints for this service:
- `main.py`: The entrypoint to start the FastAPI main service.
- `worker.py`: A worker module that consumes messages put on the redis queue. 

### The Task table in PostgreSQL
Here are the fields of the table:
- `id`: (UUID, string)
- `message`: (string)
- `status`: (string, allowed values are "pending", "canceled", "processing", "completed")
- `created_at`: (timestamp) 
- `updated_at`: (timestamp) 

### API Overview:
**`POST /tasks`: Create task queue**

This API does the following things:
1. Create a `Task` object on the database.
2. Enqueue a message to redis
Example Payload:
```json
{"message": "Hello World"}
```

Example Response:
```json
{
	"id": "5caac6f7-b5ff-4353-bee4-7fb06a31ea26",
	"message": "Hello World",
	"status": "pending",
	"created_at": "2024-10-23T08:19:44.497691",
	"updated_at": "2024-10-23T08:19:44.497691"
}
```
**`PATCH /tasks/{task_id}`: Cancel task by ID**

This API will change the status to "canceled".

Example Payload:
```json
{
	"status": "canceled"
}
```
Example Response:
```json
{
	"id": "5caac6f7-b5ff-4353-bee4-7fb06a31ea26",
	"message": "Hello World",
	"status": "canceled",
	"created_at": "2024-10-23T08:19:44.497691",
	"updated_at": "2024-10-23T08:19:44.497691"
}
```

## Task Worker
The task worker is `worker.py`.

The worker first starts 2 endless coroutines:
### `pull_messages_from_redis()`: 
It continously check if there are pending items on the redis queue. Pull the message and put on a local queue.
### `schedule_task_to_worker()`:
This is a scheduler coroutine.

It continously check if there are items in the local queue. A global variable `concuruent_task_count` is used to count how many tasks have been scheduled to the event loop.

For each worker, it can't run more than concurrent tasks based on the setting on `settings.WORKER_QUEUE_MAXSIZE`.

This is for performance concern. It's possible to set custom value by `export WORKER_QUEUE_MAXSIZE=${A_OPTIMAL_VALUE}` to tune.

With this design, there can be multiple worker running concurrently without affecting each other.

It uses `asyncio.gather()` to fire the tasks to run in parallel as soon as it has pull the maximum amount of messages.

### Gracefully shutdown feature
The worker can be stopped when the container is exitted or by sending `SIGINT`, `SIGTERM`.

When the worker receive the signal, it stop scheduling new tasks and wait for the existing tasks to finish.

This can avoid unexpected data loss.


## Other Technical Implementation to Hightlight
- Use SQLAlchemy for ORM
- Use asyncpg as PostgreSQL connection driver

## How to use the service
Build docker image
```bash
docker-compose build api-server
```

Start the service
```bash
docker-compose up -d
```

Monitor api-server's log
```bash
docker logs -f fastapi_demo-api-server-1
```

Use this link to View API spec
```
http://localhost:8000/docs
```

Start worker in a separate shell to consume the messages put in the queue
```bash
 docker exec -it fastapi_demo-api-server-1 python worker.py
 ```

Run test cases
```bash
docker exec -it fastapi_demo-api-server-1 pytest tasks/tests
```

Stop the service
```bash
docker-compose down -v
```

