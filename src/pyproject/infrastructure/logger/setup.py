import logging
import sys
import uuid
from logging.handlers import RotatingFileHandler
from typing import Any

import orjson
import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer
from structlog.typing import EventDict, WrappedLogger

from .config import LoggerConfig


def setup_logger(config: LoggerConfig) -> None:
    _setup_structlog(config)
    _setup_logging(config)


def _setup_structlog(config: LoggerConfig) -> None:
    processors = [
        *_build_default_processors(config),
        structlog.processors.StackInfoRenderer(),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.UnicodeDecoder(),  # convert bytes to str
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,  # for integration with default logging
    ]

    structlog.configure_once(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def _setup_logging(config: LoggerConfig) -> None:
    renderer_processor = JSONRenderer(_serialize_to_json) if config.json else ConsoleRenderer()
    default_processors = _build_default_processors(config)

    logging_processors = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        renderer_processor,
    ]

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=default_processors,
        processors=logging_processors,
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.set_name("default")
    handler.setLevel(config.level)
    handler.setFormatter(formatter)
    handlers: list[logging.Handler] = [handler]

    if config.file:
        file_handler = RotatingFileHandler(
            filename=config.file.path,
            maxBytes=config.file.max_size_bytes,
            backupCount=config.file.backup_count,
            encoding="utf-8",
        )
        file_handler.set_name("file")
        file_handler.setLevel(config.level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    logging.basicConfig(handlers=handlers, level=config.level)


def additional_serialize(_logger: WrappedLogger, _name: str, event_dict: EventDict) -> EventDict:
    for key, value in event_dict.items():
        if isinstance(value, uuid.UUID):
            event_dict[key] = str(value)

    return event_dict


def _build_default_processors(config: LoggerConfig) -> list[Any]:
    pr = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.ExtraAdder(),
        additional_serialize,
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=True),
        structlog.processors.dict_tracebacks,
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.PATHNAME,
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.THREAD,
                structlog.processors.CallsiteParameter.THREAD_NAME,
                structlog.processors.CallsiteParameter.PROCESS,
                structlog.processors.CallsiteParameter.PROCESS_NAME,
            },
        ),
    ]
    if config.json:
        pr.insert(0, structlog.processors.format_exc_info)

    return pr


def _serialize_to_json(data: Any, default: Any) -> str:
    return orjson.dumps(data, default=default).decode("utf-8")  # type: ignore[no-any-return]
