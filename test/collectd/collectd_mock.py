from . import register
from . import logger


class CollecdMock:

    def debug(self, msg):
        logger.debug(msg)

    def info(self, msg):
        logger.info(msg)

    def warning(self, msg):
        logger.warning(msg)

    def error(self, msg):
        logger.error(msg)

    def register_config(self, func):
        register.register_config(func)

    def register_init(self, func):
        register.register_init(func)

    def register_write(self, func):
        register.register_write(func)
