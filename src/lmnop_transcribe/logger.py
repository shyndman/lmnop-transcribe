import os
import sys

from loguru import logger

from .config import Config


def initialize_logging(config: Config):
  logger.remove()
  logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> <dim>[%d]</dim> <level>{level.icon} {message}</level>"
    % os.getpid(),
    level=config.log_level,
  )
