# -*- coding: utf-8 -*-

import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/src')

import pytest
from metrics_config import MetricsConfig, ConfigOptions
from collectd.collectd_config import CollectdConfig, ConfigNode
from collectd.helper import Helper


def test_parse_types_db():
    met_config = MetricsConfig()
    config = CollectdConfig([Helper.url_node(), Helper.types_db_node()])
    met_config.parse_config(config)

    assert len(met_config.types) == 271


def test_parse_url():
    met_config = MetricsConfig()
    config = CollectdConfig([Helper.url_node(), Helper.types_db_node()])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.url] == Helper.url


def test_parse_dimension_tags():
    met_config = MetricsConfig()
    tags = ('dim_key1', 'dim_val1', 'dim_key2', 'dim_val2')
    config = CollectdConfig([Helper.url_node(), Helper.types_db_node(),
                             tags_node(ConfigOptions.dimension_tags, tags)])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.dimension_tags] == tuple_to_pair(tags)


def test_parse_meta_tags():
    met_config = MetricsConfig()
    tags = ('meta_key1', 'meta_val1', 'meta_key2', 'meta_val2')
    config = CollectdConfig([Helper.url_node(), Helper.types_db_node(),
                             tags_node(ConfigOptions.meta_tags, tags)])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.meta_tags] == tuple_to_pair(tags)


def test_parse_meta_tags_missing_value():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        tags = ('meta_key1', 'meta_val1', 'meta_key2')
        config = CollectdConfig([Helper.url_node(), Helper.types_db_node(),
                                 tags_node(ConfigOptions.meta_tags, tags)])
        met_config.parse_config(config)

    assert "Missing tags key/value in options ('meta_key1', 'meta_val1', 'meta_key2')." in str(e.value)


def test_parse_http_post_interval():
    met_config = MetricsConfig()
    http_post_interval = '0.5'
    http_post_interval_node = ConfigNode(ConfigOptions.http_post_interval, [http_post_interval])
    config = CollectdConfig([Helper.url_node(), Helper.types_db_node(),
                             http_post_interval_node])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.http_post_interval] == float(http_post_interval)


def test_parse_http_post_interval_exception():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        http_post_interval = '0'
        http_post_interval_node = ConfigNode(ConfigOptions.http_post_interval, [http_post_interval])
        config = CollectdConfig([Helper.url_node(), Helper.types_db_node(),
                                 http_post_interval_node])
        met_config.parse_config(config)

    assert 'Value 0.0 for key HttpPostInterval is not a positive number' in str(e.value)


def test_parse_string_config():
    met_config = MetricsConfig()

    configs = {
        'source_name': 'test_source',
        'host_name': 'test_host',
        'source_category': 'test_category'
    }

    Helper.parse_configs(met_config, configs)

    for (key, value) in configs.items():

        assert met_config.conf[getattr(ConfigOptions, key)] == value


def test_parse_int_config():
    met_config = MetricsConfig()

    configs = {
        'max_batch_size': '10',
        'max_batch_interval': '5',
        'retry_initial_delay': '2',
        'retry_max_attempts': '5',
        'retry_max_delay': '10',
        'retry_backoff': '3',
        'retry_jitter_min': '1',
        'retry_jitter_max': '5',
        'max_requests_to_buffer': '100'
    }

    Helper.parse_configs(met_config, configs)

    for (key, value) in configs.items():

        assert met_config.conf[getattr(ConfigOptions, key)] == int(value)


def test_parse_retry_config_values_positive():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        configs = {
            'max_batch_size': '10',
            'max_batch_interval': '-5'
        }
        Helper.parse_configs(met_config, configs)

    assert 'Value -5 for key MaxBatchInterval is not a positive number' in str(e.value)


def test_parse_retry_config_values_non_negative():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        configs = {
            'retry_initial_delay': '-1'
        }
        Helper.parse_configs(met_config, configs)

    assert 'Value -1 for key RetryInitialDelay is a negative number' in str(e.value)


def test_parse_retry_config_jitter_min_greater_than_max():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        configs = {
            'retry_jitter_min': '2',
            'retry_jitter_max': '1'
        }
        Helper.parse_configs(met_config, configs)

    assert 'Specify RetryJitterMin 2 to be less or equal to RetryJitterMax 1' in str(e.value)


def test_parse_unknown_config_option():
    met_config = MetricsConfig()
    unknown_config = 'unknown_config'
    unknown_config_node = ConfigNode('unknown_config', unknown_config)
    config = CollectdConfig([Helper.url_node(), Helper.types_db_node(), unknown_config_node])
    met_config.parse_config(config)

    assert hasattr(met_config, 'unknown_config') is False


def test_parse_string_exception():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        url_node = ConfigNode(ConfigOptions.url, [''])
        config = CollectdConfig([url_node])
        met_config.parse_config(config)

    assert 'Value for key URL cannot be empty' in str(e.value)


def test_parse_int_exception():
    with pytest.raises(ValueError):
        met_config = MetricsConfig()
        max_batch_size = ''
        max_batch_size_node = ConfigNode(ConfigOptions.max_batch_size, [max_batch_size])
        config = CollectdConfig([Helper.url_node(), Helper.types_db_node(), max_batch_size_node])
        met_config.parse_config(config)


def test_no_url_exception():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        config = CollectdConfig([Helper.types_db_node()])
        met_config.parse_config(config)

    assert 'Specify URL in collectd.conf' in str(e.value)


def test_no_types_db_exception():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        config = CollectdConfig([Helper.url_node()])
        met_config.parse_config(config)

    assert 'Specify TypesDB in collectd.conf' in str(e.value)


def test_invalid_http_post_interval_exception():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        http_post_interval = '100.0'
        http_post_interval_node = ConfigNode(ConfigOptions.http_post_interval, [http_post_interval])
        config = CollectdConfig([Helper.url_node(), Helper.types_db_node(),
                                 http_post_interval_node])
        met_config.parse_config(config)

    assert 'Specify HttpPostInterval' in str(e.value)


def test_contains_reserved_symbols_exception():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        tags = ('meta_key1', 'meta_val1', 'meta_key2', 'meta val2')
        config = CollectdConfig([Helper.url_node(), Helper.types_db_node(),
                                 tags_node(ConfigOptions.meta_tags, tags)])
        met_config.parse_config(config)

    assert 'Value meta val2 for Key Metadata must not contain reserved symbol " "' in str(e.value)


def test_invalid_ds_in_types_db():
    met_config = MetricsConfig()
    types_db_node = ConfigNode(ConfigOptions.types_db, [cwd + '/test/types_invalid_ds.db'])
    config = CollectdConfig([Helper.url_node(), types_db_node])
    met_config.parse_config(config)

    assert 'bytes' not in met_config.conf.keys()


def test_types_db_no_exist_exception():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        types_db_node = ConfigNode(ConfigOptions.types_db, [cwd + '/test/types_not_exist.db'])
        config = CollectdConfig([Helper.url_node(), types_db_node])
        met_config.parse_config(config)

    assert 'No such file or directory' in str(e.value)


def test_non_ascii_strings():
    met_config = MetricsConfig()

    configs = {
        'source_name': '数据源',
    }

    Helper.parse_configs(met_config, configs)

    assert met_config.conf[ConfigOptions.source_name] == '数据源'



def tags_node(key, values):
    return ConfigNode(key, values)


def tuple_to_pair(tags):
    return zip(*(iter(tags),) * 2)