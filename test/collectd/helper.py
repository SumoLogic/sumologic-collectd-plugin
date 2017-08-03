import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/src')
from metrics_config import MetricsConfig, ConfigOptions
from collectd.collectd_config import CollectdConfig, ConfigNode
from collectd.data import Data


class TestHelper:

    url = "http://www.sumologic.com"

    def __del__(self):
        self.conf = TestHelper.test_config()

    @staticmethod
    def types_db_node():
        types_db = cwd + '/test/types.db'
        return ConfigNode(ConfigOptions.types_db, [types_db])

    @staticmethod
    def url_node():
        return ConfigNode(ConfigOptions.url, [TestHelper.url])

    @staticmethod
    def data_to_metric_str(data):
        pass

    @staticmethod
    def test_config():
        met_config = MetricsConfig()
        config = CollectdConfig([TestHelper.url_node(), TestHelper.types_db_node()])
        met_config.parse_config(config)
        return met_config
