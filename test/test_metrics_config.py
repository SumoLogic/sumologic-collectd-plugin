import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/src')
import pytest
from metrics_config import MetricsConfig, ConfigOptions
from collectd.collectd_config import CollectdConfig, ConfigNode

url = "http://www.sumologic.com"


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
    tags = ('dim_key1', 'dim_val1', 'dim_key2', 'dim_val2')
    config = CollectdConfig([url_node(), tags_node(ConfigOptions.dimension_tags, tags)])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.dimension_tags] == tuple_to_dict(tags)


def test_parse_meta_tags():
    met_config = MetricsConfig()
    tags = ('meta_key1', 'meta_val1', 'meta_key2', 'meta_val2')
    config = CollectdConfig([url_node(), tags_node(ConfigOptions.meta_tags, tags)])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.meta_tags] == tuple_to_dict(tags)


def test_parse_source_name():
    met_config = MetricsConfig()
    source_name = 'test_source'
    source_name_node = ConfigNode(ConfigOptions.source_name, [source_name])
    config = CollectdConfig([url_node(), source_name_node])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.source_name] == source_name


def test_parse_host_name():
    met_config = MetricsConfig()
    host_name = 'test_host'
    host_name_node = ConfigNode(ConfigOptions.host_name, [host_name])
    config = CollectdConfig([url_node(), host_name_node])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.host_name] == host_name


def test_parse_source_category():
    met_config = MetricsConfig()
    source_category = 'test_category'
    source_category_node = ConfigNode(ConfigOptions.source_category, [source_category])
    config = CollectdConfig([url_node(), source_category_node])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.source_category] == source_category


def test_parse_http_post_interval():
    met_config = MetricsConfig()
    http_post_interval = '0.5'
    http_post_interval_node = ConfigNode(ConfigOptions.http_post_interval, [http_post_interval])
    config = CollectdConfig([url_node(), http_post_interval_node])
    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.http_post_interval] == float(http_post_interval)


def test_parse_int_config():
    met_config = MetricsConfig()

    max_batch_size = '10'
    max_batch_interval = '5'
    retry_initial_delay = '2'
    retry_max_attempts = '5'
    retry_max_delay = '10'
    retry_backoff = '3'
    retry_jitter_min = '1'
    retry_jitter_max = '5'
    max_requests_to_buffer = '100'

    max_batch_size_node = ConfigNode(ConfigOptions.max_batch_size, [max_batch_size])
    max_batch_interval_node = ConfigNode(ConfigOptions.max_batch_interval, [max_batch_interval])
    retry_initial_delay_node = ConfigNode(ConfigOptions.retry_initial_delay, [retry_initial_delay])
    retry_max_attempts_node = ConfigNode(ConfigOptions.retry_max_attempts, [retry_max_attempts])
    retry_max_delay_node = ConfigNode(ConfigOptions.retry_max_delay, [retry_max_delay])
    retry_backoff_node = ConfigNode(ConfigOptions.retry_backoff, [retry_backoff])
    retry_jitter_min_node = ConfigNode(ConfigOptions.retry_jitter_min, [retry_jitter_min])
    retry_jitter_max_node = ConfigNode(ConfigOptions.retry_jitter_max, [retry_jitter_max])
    max_requests_to_buffer_node = ConfigNode(ConfigOptions.max_requests_to_buffer, [max_requests_to_buffer])

    config = CollectdConfig([url_node(), max_batch_size_node, max_batch_interval_node,
                             retry_initial_delay_node, retry_max_attempts_node,
                             retry_max_delay_node, retry_backoff_node, retry_jitter_min_node,
                             retry_jitter_max_node, max_requests_to_buffer_node])

    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.max_batch_size] == int(max_batch_size)
    assert met_config.conf[ConfigOptions.max_batch_interval] == int(max_batch_interval)
    assert met_config.conf[ConfigOptions.retry_initial_delay] == int(retry_initial_delay)
    assert met_config.conf[ConfigOptions.retry_max_attempts] == int(retry_max_attempts)
    assert met_config.conf[ConfigOptions.retry_max_delay] == int(retry_max_delay)
    assert met_config.conf[ConfigOptions.retry_backoff] == int(retry_backoff)
    assert met_config.conf[ConfigOptions.retry_jitter_min] == int(retry_jitter_min)
    assert met_config.conf[ConfigOptions.retry_jitter_max] == int(retry_jitter_max)
    assert met_config.conf[ConfigOptions.max_requests_to_buffer] == int(max_requests_to_buffer)


def test_parse_batch_config():
    met_config = MetricsConfig()

    max_batch_size = '10'
    max_batch_interval = '5'
    max_batch_size_node = ConfigNode(ConfigOptions.max_batch_size, [max_batch_size])
    max_batch_interval_node = ConfigNode(ConfigOptions.max_batch_interval, [max_batch_interval])
    config = CollectdConfig([url_node(), max_batch_size_node, max_batch_interval_node])

    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.max_batch_size] == int(max_batch_size)
    assert met_config.conf[ConfigOptions.max_batch_interval] == int(max_batch_interval)


def test_parse_retry_config():
    met_config = MetricsConfig()

    retry_initial_delay = '2'
    retry_max_attempts = '5'
    retry_max_delay = '10'
    retry_backoff = '3'
    retry_jitter_min = '1'
    retry_jitter_max = '5'

    retry_initial_delay_node = ConfigNode(ConfigOptions.retry_initial_delay, [retry_initial_delay])
    retry_max_attempts_node = ConfigNode(ConfigOptions.retry_max_attempts, [retry_max_attempts])
    retry_max_delay_node = ConfigNode(ConfigOptions.retry_max_delay, [retry_max_delay])
    retry_backoff_node = ConfigNode(ConfigOptions.retry_backoff, [retry_backoff])
    retry_jitter_min_node = ConfigNode(ConfigOptions.retry_jitter_min, [retry_jitter_min])
    retry_jitter_max_node = ConfigNode(ConfigOptions.retry_jitter_max, [retry_jitter_max])
    config = CollectdConfig([url_node(), retry_initial_delay_node, retry_max_attempts_node,
                             retry_max_delay_node, retry_backoff_node, retry_jitter_min_node,
                             retry_jitter_max_node])

    met_config.parse_config(config)

    assert met_config.conf[ConfigOptions.retry_initial_delay] == int(retry_initial_delay)
    assert met_config.conf[ConfigOptions.retry_max_attempts] == int(retry_max_attempts)
    assert met_config.conf[ConfigOptions.retry_max_delay] == int(retry_max_delay)
    assert met_config.conf[ConfigOptions.retry_backoff] == int(retry_backoff)
    assert met_config.conf[ConfigOptions.retry_jitter_min] == int(retry_jitter_min)


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
        config = CollectdConfig([url_node(), max_batch_size_node])
        met_config.parse_config(config)


def test_no_url_exception():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        del met_config.conf[ConfigOptions.url]
        config = CollectdConfig([])
        met_config.parse_config(config)

    assert 'Specify URL in collectd.conf' in str(e.value)


def test_invalid_http_post_interval_exception():
    with pytest.raises(Exception) as e:
        met_config = MetricsConfig()
        http_post_interval = '100.0'
        http_post_interval_node = ConfigNode(ConfigOptions.http_post_interval, [http_post_interval])
        config = CollectdConfig([url_node(), http_post_interval_node])
        met_config.parse_config(config)

    assert 'Specify HttpPostInterval' in str(e.value)


def tags_node(key, values):
    return ConfigNode(key, values)


def types_db_node():
    types_db = cwd + '/test/types.db'
    return ConfigNode(ConfigOptions.types_db, [types_db])


def url_node():
    return ConfigNode(ConfigOptions.url, [url])


def tuple_to_dict(tags):
    return dict(zip(*(iter(tags),) * 2))