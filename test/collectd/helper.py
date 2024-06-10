# -*- coding: utf-8 -*-

import os

from sumologic_collectd_metrics.metrics_batcher import MetricsBatcher
from sumologic_collectd_metrics.metrics_buffer import MetricsBuffer
from sumologic_collectd_metrics.metrics_config import ConfigOptions, MetricsConfig
from sumologic_collectd_metrics.metrics_sender import MetricsSender
from sumologic_collectd_metrics.metrics_writer import MetricsWriter

from . import CollecdMock
from .collectd_config import CollectdConfig, ConfigNode

cwd = os.getcwd()


class Helper:

    url = "http://www.sumologic.com"

    def __init__(self):
        config = Helper.default_config()
        self.conf = config.conf

    @staticmethod
    def default_config():
        met_config = MetricsConfig(CollecdMock())
        config = CollectdConfig([Helper.url_node()])
        met_config.parse_config(config)
        return met_config

    @staticmethod
    def get_buffer(size):
        return MetricsBuffer(size, CollecdMock())

    @staticmethod
    def get_batcher(max_batch_size, interval, met_buffer):
        return MetricsBatcher(max_batch_size, interval, met_buffer, CollecdMock())

    @staticmethod
    def get_sender(conf, buffer):
        return MetricsSender(conf, buffer, CollecdMock())

    @staticmethod
    def default_buffer():
        return MetricsBuffer(10, CollecdMock())

    @staticmethod
    def default_writer():
        return MetricsWriter(CollecdMock())

    @staticmethod
    def url_node():
        return ConfigNode(ConfigOptions.url, [Helper.url])

    @staticmethod
    def enable_internal_metrics_node():
        return ConfigNode(ConfigOptions.enable_internal_metrics, [True])

    @staticmethod
    def signalfx_statsd_tags_node():
        return ConfigNode(ConfigOptions.signalfx_statsd_tags, [True])

    @staticmethod
    def parse_configs(met_config, configs):
        for key, value in configs.items():
            node = ConfigNode(getattr(ConfigOptions, key), [value])
            config = CollectdConfig([Helper.url_node(), node])
            met_config.parse_config(config)
