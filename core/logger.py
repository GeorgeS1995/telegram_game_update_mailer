import os
import sys
from loguru import logger

LOG_LEVEL = os.getenv('LOG_LEVEL')

if LOG_LEVEL not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
    logger.critical("Please set a logger level by setting a system LOG_LEVEL env."
                    " Allowed value: DEBUG, INFO, WARNING, ERROR, CRITICAL")
    exit(1)

logger.remove()
logger.add(sys.stdout, level=LOG_LEVEL)
project_dir = os.path.dirname(os.path.realpath(__file__))
logger.add(os.path.join(project_dir, "../logs", "file_{time}.log"), level=LOG_LEVEL, rotation="10 MB",
           compression="tar.bz2")
