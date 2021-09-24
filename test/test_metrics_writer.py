# -*- coding: utf-8 -*-

import time

import pytest

from collectd import Helper
from collectd.collectd_config import CollectdConfig
from collectd.values import Values
from sumologic_collectd_metrics.metrics_config import ConfigOptions


def test_config_callback():
    metrics_writer = Helper.default_writer()
    config = CollectdConfig([Helper.url_node()])
    metrics_writer.parse_config(config)

    metrics_writer.met_config.conf[ConfigOptions.url] = Helper.url


def test_init_callback():
    metrics_writer = Helper.default_writer()
    config = CollectdConfig([Helper.url_node()])
    metrics_writer.parse_config(config)
    metrics_writer.init_callback()
    assert metrics_writer.met_buffer is not None
    assert metrics_writer.met_batcher is not None
    assert metrics_writer.met_sender is not None


def test_write_callback():
    metrics_writer = Helper.default_writer()
    config = CollectdConfig([Helper.url_node()])
    metrics_writer.parse_config(config)
    metrics_writer.init_callback()
    data = Values()
    metrics_writer.write_callback(data)
    assert metrics_writer.met_batcher.queue.qsize() == 1
    assert [metrics_writer.met_batcher.queue.get()] == data.metrics_str()


def test_write_callback_host_with_equal_char():
    metrics_writer = Helper.default_writer()
    config = CollectdConfig([Helper.url_node()])
    metrics_writer.parse_config(config)
    metrics_writer.init_callback()
    data = Values(host="[invalid=host]")
    expected_value = ['host=[invalid:host]' \
    ' plugin=test_plugin plugin_instance=test_plugin_instance' \
    ' type=test_type type_instance=test_type_instance ds_name=test_ds_name ds_type=test_ds_type' \
    ' metric=test_type.test_type_instance  test_meta_key=test_meta_val 3.140000 1501775008']
    metrics_writer.write_callback(data)

    assert metrics_writer.met_batcher.queue.qsize() == 1
    assert [metrics_writer.met_batcher.queue.get()] == expected_value


def test_write_callback_boolean_value():
    metrics_writer = Helper.default_writer()
    config = CollectdConfig([Helper.url_node()])
    metrics_writer.parse_config(config)
    metrics_writer.init_callback()
    data = Values(values=[True])
    metrics_writer.write_callback(data)
    assert metrics_writer.met_batcher.queue.qsize() == 1
    assert [metrics_writer.met_batcher.queue.get()] == data.metrics_str()


def test_write_callback_boolean_tag():
    metrics_writer = Helper.default_writer()
    config = CollectdConfig([Helper.url_node()])
    metrics_writer.parse_config(config)
    metrics_writer.init_callback()
    data = Values(host=True)
    metrics_writer.write_callback(data)
    assert metrics_writer.met_batcher.queue.qsize() == 1
    assert [metrics_writer.met_batcher.queue.get()] == data.metrics_str()


def test_write_callback_invalid_metric_name():
    with pytest.raises(Exception) as e:
        metrics_writer = Helper.default_writer()
        config = CollectdConfig([Helper.url_node()])
        metrics_writer.parse_config(config)
        metrics_writer.init_callback()
        data = Values(type='test')
        metrics_writer.write_callback(data)

    assert 'Do not know how to handle type test' in str(e)


def test_shutdown_call_back():
    metrics_writer = Helper.default_writer()
    config = CollectdConfig([Helper.url_node()])
    metrics_writer.parse_config(config)
    metrics_writer.init_callback()

    for i in range(10):
        metrics_writer.met_buffer.put_pending_batch(['batch_%s' % i])

    metrics_writer.shutdown_callback()

    time.sleep(2)

    assert metrics_writer.met_buffer.empty() is True


def test_register():
    metrics_writer = Helper.default_writer()
    metrics_writer.register()
