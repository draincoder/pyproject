from dataclasses import dataclass

from pyproject.infrastructure.logger import LoggerConfig


@dataclass(frozen=True, slots=True)
class AppConfig:
    logger: LoggerConfig
