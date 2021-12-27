# -*- coding: utf-8 -*-

from . import logger, register


class CollecdMock:
    TYPES = {
        "test_type": [("test_ds_name", "test_ds_type", 0, None)],
        "test_type_2": [
            ("test_ds_name1", "test_ds_type1", 0, None),
            ("test_ds_name2", "test_ds_type2", 0, None),
        ],
    }

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

    def register_shutdown(self, func):
        register.register_shutdown(func)

    def get_dataset(self, name):
        try:
            return self.TYPES[name]
        except KeyError:
            raise TypeError("Unknown type")
