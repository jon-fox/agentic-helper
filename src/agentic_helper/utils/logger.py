from __future__ import annotations

import logging
import os
import sys

_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_DEFAULT_LEVEL = "INFO"


def get_logger(name: str = "agentic_helper", level: int | str | None = None) -> logging.Logger:
    """
    Return a logger that writes to stdout.
    """
    logger = logging.getLogger(name)

    if level is None:
        level = os.environ.get("HELPER_LOG_LEVEL", _DEFAULT_LEVEL)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
        logger.addHandler(handler)
        logger.propagate = False

    return logger
