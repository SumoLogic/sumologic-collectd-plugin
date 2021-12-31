# -*- coding: utf-8 -*-

import logging

# We use logging here so we can easily make assertions using pytest's caplog fixture
logger = logging.getLogger("collectd")


def debug(msg):
    logger.debug(msg)


def info(msg):
    logger.info(msg)


def warning(msg):
    logger.warning(msg)


def error(msg):
    logger.error(msg)
