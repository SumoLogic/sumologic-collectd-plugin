import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/src')
from metrics_config import MetricsConfig, ConfigOptions
from collectd.collectd_config import CollectdConfig, ConfigNode

url = "http://www.sumologic.com"
types_db = cwd + '/test/types.db'


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


def test_parse_dimension_tags():
    met_config = MetricsConfig()
    tags = ['dim_key1', 'dim_val1', 'dim_key2', 'dim_val2']
    config = CollectdConfig([url_node(), tags_node(ConfigOptions.dimension_tags, tags)])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.dimension_tags] == list_to_dict(tags)


def test_parse_meta_tags():
    met_config = MetricsConfig()
    tags = ['meta_key1', 'meta_val1', 'meta_key2', 'meta_val2']
    config = CollectdConfig([url_node(), tags_node(ConfigOptions.meta_tags, tags)])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.meta_tags] == list_to_dict(tags)


def tags_node(key, values):
    return ConfigNode(key, values)


def types_db_node():
    return ConfigNode(ConfigOptions.types_db, [types_db])


def url_node():
    return ConfigNode(ConfigOptions.url, [url])


def list_to_dict(tags):
    return dict(zip(*(iter(tags),) * 2))