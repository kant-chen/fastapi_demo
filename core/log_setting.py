log_setting = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s.%(msecs)03d %(name)s %(levelname)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "file_handler": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "debug.log",
        },
    },
    "loggers": {
        "api_server": {"level": "INFO", "handlers": ["console"], "propagate": "no"},
        "asyncio": {"level": "WARNING", "handlers": ["console"], "propagate": "no"}
    },
    # "root": {"level": "DEBUG", "handlers": ["console", "file_handler"]},
}
