import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/src')
from metrics_config import MetricsConfig, ConfigOptions
from collectd.collectd_config import CollectdConfig, ConfigNode


class Helper:

    url = 'http://www.sumologic.com'
    types_db = cwd + '/test/types.db'

    def __init__(self):
        config = Helper.default_config()
        self.conf = config.conf
        self.types = config.types

    @staticmethod
    def types_db_node():
        return ConfigNode(ConfigOptions.types_db, [Helper.types_db])

    @staticmethod
    def url_node():
        return ConfigNode(ConfigOptions.url, [Helper.url])

    @staticmethod
    def default_config():
        met_config = MetricsConfig()
        config = CollectdConfig([Helper.url_node(), Helper.types_db_node()])
        met_config.parse_config(config)
        return met_config

    @staticmethod
    def parse_configs(met_config, configs):
        for (key, value) in configs.items():
            node = ConfigNode(getattr(ConfigOptions, key), [value])
            config = CollectdConfig([Helper.url_node(), node])
            met_config.parse_config(config)
