import logging

from pyproject.config import AppConfig
from pyproject.infrastructure.config import load_config
from pyproject.infrastructure.logger import setup_logger

logger = logging.getLogger(__name__)


def main() -> None:
    config = load_config(AppConfig)
    setup_logger(config.logger)

    logger.info("Application started")
    logger.info("Application stopped")


if __name__ == "__main__":
    main()
