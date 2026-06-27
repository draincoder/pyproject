import json
import logging
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
import structlog

from pyproject.infrastructure.logger import FileLoggerConfig, LoggerConfig, setup_logger


@pytest.fixture(autouse=True)
def reset_logging_state() -> Iterator[None]:
    structlog.reset_defaults()
    logging.basicConfig(handlers=[], force=True)

    yield

    structlog.reset_defaults()
    logging.basicConfig(handlers=[], force=True)


def raise_value_error() -> None:
    msg = "boom"
    raise ValueError(msg)


def flush_handlers() -> None:
    for handler in logging.getLogger().handlers:
        handler.flush()


def test_plain_structlog_logger_writes_formatted_message_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    # Arrange
    config = LoggerConfig(file=FileLoggerConfig(), json=False)
    setup_logger(config)

    # Act
    structlog.get_logger("demo").info("hello %s", "world")

    # Assert
    captured = capsys.readouterr()
    assert "hello world" in captured.out


def test_plain_stdlib_logger_formats_traceback(capsys: pytest.CaptureFixture[str]) -> None:
    # Arrange
    config = LoggerConfig(file=FileLoggerConfig(), json=False)
    setup_logger(config)

    # Act
    try:
        raise_value_error()
    except ValueError:
        logging.getLogger("demo").exception("plain failure")

    # Assert
    captured = capsys.readouterr()
    assert "plain failure" in captured.out
    assert "ValueError: boom" in captured.out


def test_json_structlog_logger_writes_serialized_event_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    # Arrange
    request_id = uuid.UUID("12345678-1234-5678-1234-567812345678")
    config = LoggerConfig(file=FileLoggerConfig(), json=True)
    setup_logger(config)

    # Act
    try:
        raise_value_error()
    except ValueError:
        structlog.get_logger("demo").exception("json %s", "failure", request_id=request_id)

    # Assert
    captured = capsys.readouterr()
    event = json.loads(captured.out)
    assert event["msg"] == "json failure"
    assert event["request_id"] == str(request_id)
    assert isinstance(event["exception"], str)
    assert "ValueError: boom" in event["exception"]


def test_json_stdlib_logger_writes_extra_fields_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    # Arrange
    request_id = uuid.UUID("87654321-4321-8765-4321-876543218765")
    config = LoggerConfig(file=FileLoggerConfig(), json=True)
    setup_logger(config)

    # Act
    logging.getLogger("demo").info("stdlib json message", extra={"request_id": request_id})

    # Assert
    captured = capsys.readouterr()
    event = json.loads(captured.out)
    assert event["msg"] == "stdlib json message"
    assert event["request_id"] == str(request_id)
    assert event["level"] == "info"


def test_file_logger_writes_plain_message_to_stdout_and_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # Arrange
    log_path = tmp_path / "logs" / "app.log"
    file_config = FileLoggerConfig(enabled=True, path=str(log_path), max_size_mb=1, backup_count=1)
    config = LoggerConfig(file=file_config, json=False)
    setup_logger(config)

    # Act
    logging.getLogger("demo").warning("file message")
    flush_handlers()

    # Assert
    captured = capsys.readouterr()
    assert "file message" in captured.out
    assert "file message" in log_path.read_text()


def test_file_logger_writes_json_message_to_file(tmp_path: Path) -> None:
    # Arrange
    log_path = tmp_path / "logs" / "app.log"
    file_config = FileLoggerConfig(enabled=True, path=str(log_path), max_size_mb=1, backup_count=1)
    config = LoggerConfig(file=file_config, json=True)
    setup_logger(config)

    # Act
    structlog.get_logger("demo").info("json file message", category="audit")
    flush_handlers()

    # Assert
    event = json.loads(log_path.read_text())
    assert event["msg"] == "json file message"
    assert event["category"] == "audit"
