import logging
import sys
import uuid
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

import orjson
import structlog
from structlog.processors import JSONRenderer
from structlog.typing import EventDict, WrappedLogger

from .config import LoggerConfig


def setup_logger(config: LoggerConfig) -> None:
    _setup_structlog()
    _setup_logging(config)


def _setup_structlog() -> None:
    processors = [
        *_build_default_processors(),
        structlog.processors.StackInfoRenderer(),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure_once(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def _setup_logging(config: LoggerConfig) -> None:
    default_processors = _build_default_processors()
    stream_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=default_processors,
        processors=_build_render_processors(json=config.json, colors=True),
    )

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.set_name("default")
    stream_handler.setLevel(config.level)
    stream_handler.setFormatter(stream_formatter)
    handlers: list[logging.Handler] = [stream_handler]

    if config.file.enabled:
        Path(config.file.path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

        file_formatter = structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=default_processors,
            processors=_build_render_processors(json=config.json, colors=False),
        )
        file_handler = RotatingFileHandler(
            filename=config.file.path,
            maxBytes=config.file.max_size_bytes,
            backupCount=config.file.backup_count,
            encoding="utf-8",
        )

        file_handler.set_name("file")
        file_handler.setLevel(config.level)
        file_handler.setFormatter(file_formatter)
        handlers.append(file_handler)

    logging.basicConfig(handlers=handlers, level=config.level, force=True)


def _build_default_processors() -> list[Any]:
    processors: list[Any] = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.ExtraAdder(),
        _additional_serialize,
        structlog.dev.set_exc_info,
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
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

    return processors


def _build_render_processors(*, json: bool, colors: bool) -> list[Any]:
    processors: list[Any] = [structlog.stdlib.ProcessorFormatter.remove_processors_meta]

    if json:
        processors.append(structlog.processors.EventRenamer("msg"))
        processors.append(JSONRenderer(_serialize_to_json))
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=colors))

    return processors


def _additional_serialize(_logger: WrappedLogger, _name: str, event_dict: EventDict) -> EventDict:
    return {k: (str(v) if isinstance(v, uuid.UUID) else v) for k, v in event_dict.items()}


def _serialize_to_json(data: Any, **kwargs: Any) -> str:
    default = kwargs.get("default")
    return orjson.dumps(data, default=default).decode("utf-8")
