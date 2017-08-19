import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/sumologic_collectd_plugin')
from metrics_config import MetricsConfig, ConfigOptions
from metrics_buffer import MetricsBuffer
from metrics_batcher import MetricsBatcher
from metrics_sender import MetricsSender
from metrics_writer import MetricsWriter
from collectd.collectd_config import CollectdConfig, ConfigNode
from collectd import CollecdMock


class Helper:

    url = 'http://www.sumologic.com'
    types_db = cwd + '/test/types.db'

    def __init__(self):
        config = Helper.default_config()
        self.conf = config.conf
        self.types = config.types

    @staticmethod
    def default_config():
        met_config = MetricsConfig(CollecdMock())
        config = CollectdConfig([Helper.url_node(), Helper.types_db_node()])
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
    def types_db_node():
        return ConfigNode(ConfigOptions.types_db, [Helper.types_db])

    @staticmethod
    def url_node():
        return ConfigNode(ConfigOptions.url, [Helper.url])

    @staticmethod
    def parse_configs(met_config, configs):
        for (key, value) in configs.items():
            node = ConfigNode(getattr(ConfigOptions, key), [value])
            config = CollectdConfig([Helper.url_node(), Helper.types_db_node(), node])
            met_config.parse_config(config)
