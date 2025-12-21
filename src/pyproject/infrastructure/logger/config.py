from dataclasses import dataclass
from typing import Literal

DEFAULT_MAX_FILE_SIZE = 10
DEFAULT_BACKUP_COUNT = 10
MEGABYTE = 1024 * 1024

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


@dataclass(frozen=True, slots=True)
class FileLoggerConfig:
    enabled: bool = False
    path: str = "app.log"
    max_size_mb: int = DEFAULT_MAX_FILE_SIZE
    backup_count: int = DEFAULT_BACKUP_COUNT

    @property
    def max_size_bytes(self) -> int:
        return self.max_size_mb * MEGABYTE


@dataclass(frozen=True, slots=True)
class LoggerConfig:
    file: FileLoggerConfig
    level: LogLevel = "INFO"
    json: bool = False
