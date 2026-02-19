"""
UUP Dump API Python module.

A Python wrapper for the UUP Dump API with comprehensive error handling and logging.
"""

import logging

from .adapter import RestAdapter
from .exceptions import (
    UUPDumpAPIError,
    UUPDumpHTTPError,
    UUPDumpValidationError,
    UUPDumpTimeoutError,
    UUPDumpConnectionError,
    UUPDumpResponseError,
    get_error_message,
    API_ERROR_MESSAGES,
)

__version__ = "0.1.0"
__author__ = "Cairnstew"

# Module-level logger
logger = logging.getLogger(__name__)

# Prevent logging from propagating to root logger by default
logger.addHandler(logging.NullHandler())


def configure_logging(level=logging.INFO, format_string=None):
    """
    Configure logging for the uup_dump_api module.

    Args:
        level: Logging level (default: logging.INFO)
        format_string: Custom format string for log messages (optional)

    Example:
        >>> import uup_dump_api
        >>> uup_dump_api.configure_logging(level=logging.DEBUG)
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Remove existing handlers
    logger.handlers.clear()

    # Create and configure handler
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(format_string)
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)
    logger.setLevel(level)

    logger.info(f"Logging configured at level {logging.getLevelName(level)}")


__all__ = [
    "RestAdapter",
    "UUPDumpAPIError",
    "UUPDumpHTTPError",
    "UUPDumpValidationError",
    "UUPDumpTimeoutError",
    "UUPDumpConnectionError",
    "UUPDumpResponseError",
    "get_error_message",
    "API_ERROR_MESSAGES",
    "configure_logging",
    "__version__",
]
