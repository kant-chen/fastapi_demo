# FastAPI demo project
### Implement a high-throughput task processing app using Python FastAPI
This is a project that demonstrate how to use FastAPI to implment asynchronous APIs


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

