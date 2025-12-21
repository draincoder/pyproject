from pyproject.config import AppConfig
from pyproject.infrastructure import load_config
from pyproject.infrastructure.logger import LoggerConfig
from pyproject.infrastructure.logger.config import FileLoggerConfig


def test_config() -> None:
    # Arrange
    path = "../../config/template.config.yaml"

    # Act
    config = load_config(AppConfig, path)

    # Assert
    assert config.logger != LoggerConfig(FileLoggerConfig())
