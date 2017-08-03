import sys
sys.path.append('src')
from metrics_config import MetricsConfig, ConfigOptions
from collectd.collectd_config import CollectdConfig, ConfigNode

url = "http://www.sumologic.com"
types_db = 'test/data/types.db'


def test_parse_types_db():
    met_config = MetricsConfig()
    config = CollectdConfig([url_node(), types_db_node()])
    met_config.parse_config(config)

    assert len(met_config.types) == 269


def test_parse_url():
    met_config = MetricsConfig()
    config = CollectdConfig([url_node()])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.url] == url


def types_db_node():
    return ConfigNode(ConfigOptions.types_db, [types_db])


def url_node():
    return ConfigNode(ConfigOptions.url, [url])