from __future__ import annotations

import logging
import sys
from typing import Any

from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:  # noqa: D401
        try:
            level = logger.level(record.levelname).name
        except Exception:
            level = record.levelno
        logger.bind(logger=record.name).opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(level: str | int = "INFO") -> None:
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(level if isinstance(level, int) else logging.getLevelName(level))

    for name in (
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "sqlalchemy.engine",
    ):
        logging.getLogger(name).handlers = [InterceptHandler()]

    logger.remove()
    logger.add(sys.stdout, level=level, backtrace=False, diagnose=False, enqueue=True)
