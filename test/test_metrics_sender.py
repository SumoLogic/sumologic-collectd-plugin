import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/src')

import pytest
import requests
import time
import zlib
from metrics_config import MetricsConfig, ConfigOptions
from metrics_sender import MetricsSender, HeaderKeys
from metrics_buffer import MetricsBuffer
from collectd.collectd_config import CollectdConfig, ConfigNode
from collectd.helper import Helper


@pytest.fixture(scope="function", autouse=True)
def reset_response_decider_and_fake_server():
    requests.post_response_decider.reset()
    requests.mock_server.reset()
    requests.mock_response.reset()


def test_post_normal_no_additional_header():
    met_buffer = MetricsBuffer(10)
    helper = Helper()

    for i in range(10):
        met_buffer.put_pending_batch(['batch_%s' % i])

    met_sender = MetricsSender(helper.conf, met_buffer)

    sleep_helper(10, 0.100, 100)

    assert requests.mock_server.url == helper.conf[ConfigOptions.url]
    assert requests.mock_server.headers == {
        HeaderKeys.content_type: helper.conf[ConfigOptions.content_type],
        HeaderKeys.content_encoding: helper.conf[ConfigOptions.content_encoding]
    }
    for i in range(10):
        assert zlib.decompress(requests.mock_server.data[i]) == 'batch_%s' % i

    met_sender.cancel_timer()


def test_post_normal_additional_keys():
    met_buffer = MetricsBuffer(10)
    met_config = MetricsConfig()

    configs = {
        'source_name': 'test_source',
        'host_name': 'test_host',
        'source_category': 'test_category'
    }

    for (key, value) in configs.items():
        node = ConfigNode(getattr(ConfigOptions, key), [value])
        config = CollectdConfig([Helper.url_node(), node])
        met_config.parse_config(config)

    for i in range(10):
        met_buffer.put_pending_batch(['batch_%s' % i])

    met_sender = MetricsSender(met_config.conf, met_buffer)

    sleep_helper(10, 0.100, 100)

    assert requests.mock_server.url == met_config.conf[ConfigOptions.url]
    assert requests.mock_server.headers == {
        HeaderKeys.content_type: met_config.conf[ConfigOptions.content_type],
        HeaderKeys.content_encoding: met_config.conf[ConfigOptions.content_encoding],
        HeaderKeys.x_sumo_source: 'test_source',
        HeaderKeys.x_sumo_host: 'test_host',
        HeaderKeys.x_sumo_category: 'test_category'
    }

    for i in range(10):
        assert zlib.decompress(requests.mock_server.data[i]) == 'batch_%s' % i

    met_sender.cancel_timer()


def test_post_normal_addition_dimensions_metadata():
    met_buffer = MetricsBuffer(10)
    met_config = MetricsConfig()

    configs = {
        'dimension_tags': ('dim_key1', 'dim_val1', 'dim_key2', 'dim_val2'),
        'meta_tags': ('meta_key1', 'meta_val1', 'meta_key2', 'meta_val2')
    }

    for (key, value) in configs.items():
        node = ConfigNode(getattr(ConfigOptions, key), value)
        config = CollectdConfig([Helper.url_node(), node])
        met_config.parse_config(config)

    for i in range(10):
        met_buffer.put_pending_batch(['batch_%s' % i])

    met_sender = MetricsSender(met_config.conf, met_buffer)

    sleep_helper(10, 0.100, 100)

    assert requests.mock_server.url == met_config.conf[ConfigOptions.url]
    assert requests.mock_server.headers == {
        HeaderKeys.content_type: met_config.conf[ConfigOptions.content_type],
        HeaderKeys.content_encoding: met_config.conf[ConfigOptions.content_encoding],
        HeaderKeys.x_sumo_dimensions: 'dim_key1=dim_val1 dim_key2=dim_val2',
        HeaderKeys.x_sumo_metadata: 'meta_key1=meta_val1 meta_key2=meta_val2',
    }

    for i in range(10):
        assert zlib.decompress(requests.mock_server.data[i]) == 'batch_%s' % i

    met_sender.cancel_timer()


def test_post_client_recoverable_http_error():
    helper_test_post_recoverable_http_error(404)


def test_post_server_recoverable_http_error():
    helper_test_post_recoverable_http_error(500)


def helper_test_post_recoverable_http_error(error_code):
    met_buffer = MetricsBuffer(10)
    met_config = MetricsConfig()

    configs = {
        'retry_initial_delay': '0',
        'retry_max_attempts': '10',
        'retry_max_delay': '5',
        'retry_backoff': '1',
        'retry_jitter_min': '0',
        'retry_jitter_max': '0'
    }

    for (key, value) in configs.items():
        node = ConfigNode(getattr(ConfigOptions, key), [value])
        config = CollectdConfig([Helper.url_node(), node])
        met_config.parse_config(config)

    requests.post_response_decider.set(True, False, None, 5, 0)
    requests.mock_response.set(error_code)

    for i in range(10):
        met_buffer.put_pending_batch(['batch_%s' % i])

    met_sender = MetricsSender(met_config.conf, met_buffer)

    sleep_helper(10, 0.100, 100)

    assert requests.mock_server.url == met_config.conf[ConfigOptions.url]
    assert requests.mock_server.headers == {
        HeaderKeys.content_type: met_config.conf[ConfigOptions.content_type],
        HeaderKeys.content_encoding: met_config.conf[ConfigOptions.content_encoding]
    }

    for i in range(10):
        assert zlib.decompress(requests.mock_server.data[i]) == 'batch_%s' % i

    met_sender.cancel_timer()


def test_post_unrecoverable_http_error():
    with pytest.raises(Exception) as e:
        met_buffer = MetricsBuffer(10)
        met_config = MetricsConfig()

        configs = {
            'retry_initial_delay': '0',
            'retry_max_attempts': '10',
            'retry_max_delay': '5',
            'retry_backoff': '1',
            'retry_jitter_min': '0',
            'retry_jitter_max': '0'
        }

        for (key, value) in configs.items():
            node = ConfigNode(getattr(ConfigOptions, key), [value])
            config = CollectdConfig([Helper.url_node(), node])
            met_config.parse_config(config)

        requests.post_response_decider.set(True, False, None, 5, 0)
        requests.mock_response.set(400)

        for i in range(10):
            met_buffer.put_pending_batch(['batch_%s' % i])

        MetricsSender(met_config.conf, met_buffer)

    assert e.type is requests.exceptions.HTTPError


def test_post_recoverable_requests_exception():

    met_buffer1 = MetricsBuffer(10)
    met_config = MetricsConfig()

    configs = {
        'retry_initial_delay': '0',
        'retry_max_attempts': '10',
        'retry_max_delay': '5',
        'retry_backoff': '1',
        'retry_jitter_min': '0',
        'retry_jitter_max': '0',
        'http_post_interval': '0.5'
    }

    for (key, value) in configs.items():
        node = ConfigNode(getattr(ConfigOptions, key), [value])
        config = CollectdConfig([Helper.url_node(), node])
        met_config.parse_config(config)

    e = requests.exceptions.ConnectionError(requests.exceptions.RequestException())
    requests.post_response_decider.set(False, True, e, 5, 0)

    for i in range(10):
        met_buffer1.put_pending_batch(['batch_%s' % i])

    met_sender = MetricsSender(met_config.conf, met_buffer1)

    sleep_helper(10, 0.100, 100)

    assert requests.mock_server.url == met_config.conf[ConfigOptions.url]
    assert requests.mock_server.headers == {
        HeaderKeys.content_type: met_config.conf[ConfigOptions.content_type],
        HeaderKeys.content_encoding: met_config.conf[ConfigOptions.content_encoding]
    }

    for i in range(10):
        assert zlib.decompress(requests.mock_server.data[i]) == 'batch_%s' % i

    met_sender.cancel_timer()


def test_post_unrecoverable_requests_exception():
    pass


def test_post_fail_after_retries_with_buffer_not_full():
    pass


def test_post_fail_after_retries_with_buffer_full():
    pass


def sleep_helper(expected_data_size, sleep_interval, max_tries):
    current_retry = 0
    while len(requests.mock_server.data) != expected_data_size \
            and current_retry < max_tries:
        time.sleep(sleep_interval)
        current_retry += 1
