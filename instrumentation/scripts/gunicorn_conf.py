# GENERAL CONFIGURATION SECTION
# =============================

# DO NOT MODIFY WITHOUT A VERY GOOD REASON, MAKE SURE YOU CHECK WITH THE SOURCE:
# https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/master/docker-images/gunicorn_conf.py

import json
import multiprocessing
import os

workers_per_core_str = os.getenv("WORKERS_PER_CORE", "1")
max_workers_str = os.getenv("MAX_WORKERS")
use_max_workers = None
if max_workers_str:
    use_max_workers = int(max_workers_str)
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)

host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "80")
bind_env = os.getenv("BIND", None)
use_loglevel = os.getenv("LOG_LEVEL", "info")
if bind_env:
    use_bind = bind_env
else:
    use_bind = f"{host}:{port}"

cores = multiprocessing.cpu_count()
workers_per_core = float(workers_per_core_str)
default_web_concurrency = workers_per_core * cores
if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    web_concurrency = max(int(default_web_concurrency), 2)
    if use_max_workers:
        web_concurrency = min(web_concurrency, use_max_workers)
accesslog_var = os.getenv("ACCESS_LOG", "-")
use_accesslog = accesslog_var or None
errorlog_var = os.getenv("ERROR_LOG", "-")
use_errorlog = errorlog_var or None
graceful_timeout_str = os.getenv("GRACEFUL_TIMEOUT", "120")
timeout_str = os.getenv("TIMEOUT", "120")
keepalive_str = os.getenv("KEEP_ALIVE", "5")

# Gunicorn config variables
loglevel = use_loglevel
workers = web_concurrency
bind = use_bind
errorlog = use_errorlog
worker_tmp_dir = "/dev/shm"
accesslog = use_accesslog
graceful_timeout = int(graceful_timeout_str)
timeout = int(timeout_str)
keepalive = int(keepalive_str)


# For debugging and testing
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
    "graceful_timeout": graceful_timeout,
    "timeout": timeout,
    "keepalive": keepalive,
    "errorlog": errorlog,
    "accesslog": accesslog,
    # Additional, non-gunicorn variables
    "workers_per_core": workers_per_core,
    "use_max_workers": use_max_workers,
    "host": host,
    "port": port,
}
# disabled for now in favor of logger output
# print(json.dumps(log_data))

# LOGGING CONFIGURATION SECTION
# =============================

import logging
import os
import sys

from loguru import logger

import gunicorn.glogging


# class taken from loguru docs, DO NOT MODIFY, customizations should be done in handlers
# https://github.com/Delgan/loguru#entirely-compatible-with-standard-logging
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class InterceptedGunicornLogger(gunicorn.glogging.Logger):
    def setup(self, cfg):
        handler = InterceptHandler()
        level = logging.getLevelName(os.environ.get("LOG_LEVEL", "debug").upper())

        self.error_logger = logging.getLogger("gunicorn.error")
        self.error_logger.handlers = [handler]
        self.error_logger.setLevel(level)

        self.access_logger = logging.getLogger("gunicorn.access")
        self.access_logger.handlers = [handler]
        self.access_logger.setLevel(level)


is_deployed_locally = os.environ.get("ENVIRONMENT") in (None, "", "local", "test")
if not is_deployed_locally:
    logger.configure(handlers=[])
    logger.add(sink=sys.stderr, level=loglevel.upper(), diagnose=False, serialize=True, format="{message}")

logger_class = InterceptedGunicornLogger


# disabled for now, reloading oddly works only for the first change
# to enable, also modify the startup line in start.sh and remove the conf file option:
# exec gunicorn -c "$GUNICORN_CONF" "$APP_MODULE"

# from uvicorn.workers import UvicornWorker
#
#
# class DebugUvicornWorker(UvicornWorker):
#     CONFIG_KWARGS = UvicornWorker.CONFIG_KWARGS | dict(reload=True)
#
#
# worker_class = "scripts.gunicorn_conf.DebugUvicornWorker"
# reload = True
