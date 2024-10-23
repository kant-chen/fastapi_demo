class TaskNotfound(Exception):
    message = "Task not found in DB."


class TaskStatusUpdateNotAllowed(Exception):
    message = "The task's status is not allowed to change."