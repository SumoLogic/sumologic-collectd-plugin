# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name,no-self-use

import time

try:
    from unittest import mock
except ImportError:  # python 2
    import mock

import pytest
from collectd import Helper
from collectd.collectd_config import CollectdConfig
from collectd.values import Values

from sumologic_collectd_metrics.metrics_config import ConfigOptions
from sumologic_collectd_metrics.metrics_writer import PLUGIN_NAME


@pytest.fixture
def config():
    return CollectdConfig([Helper.url_node()])


@pytest.fixture
def metrics_writer():
    return Helper.default_writer()


@pytest.fixture
def configured_metrics_writer(metrics_writer, config):
    metrics_writer.parse_config(config)
    return metrics_writer


@pytest.fixture
def initialized_metrics_writer(configured_metrics_writer):
    configured_metrics_writer.init_callback()
    return configured_metrics_writer


def test_config_callback(metrics_writer):
    config = CollectdConfig([Helper.url_node()])
    metrics_writer.parse_config(config)
    assert metrics_writer.met_config.conf[ConfigOptions.url] == Helper.url


def test_init_callback(configured_metrics_writer):
    metrics_writer = configured_metrics_writer
    metrics_writer.init_callback()
    assert metrics_writer.met_buffer is not None
    assert metrics_writer.met_batcher is not None
    assert metrics_writer.met_sender is not None


def test_write_callback(initialized_metrics_writer):
    metrics_writer = initialized_metrics_writer
    data = Values()
    metrics_writer.write_callback(data)
    assert metrics_writer.met_batcher.queue.qsize() == 1
    assert [metrics_writer.met_batcher.queue.get()] == data.metrics_str()


def test_write_callback_host_with_equal_char(initialized_metrics_writer):
    metrics_writer = initialized_metrics_writer
    data = Values(host="[invalid=host]")
    expected_value = [
        "host=[invalid:host]"
        " plugin=test_plugin plugin_instance=test_plugin_instance"
        " type=test_type type_instance=test_type_instance ds_name=test_ds_name ds_type=test_ds_type"
        " metric=test_type.test_type_instance  test_meta_key=test_meta_val 3.140000 1501775008"
    ]
    metrics_writer.write_callback(data)

    assert metrics_writer.met_batcher.queue.qsize() == 1
    assert [metrics_writer.met_batcher.queue.get()] == expected_value


def test_write_callback_boolean_value(initialized_metrics_writer):
    metrics_writer = initialized_metrics_writer
    data = Values(values=[True])
    metrics_writer.write_callback(data)
    assert metrics_writer.met_batcher.queue.qsize() == 1
    assert [metrics_writer.met_batcher.queue.get()] == data.metrics_str()


def test_write_callback_boolean_tag(initialized_metrics_writer):
    metrics_writer = initialized_metrics_writer
    data = Values(host=True)
    metrics_writer.write_callback(data)
    assert metrics_writer.met_batcher.queue.qsize() == 1
    assert [metrics_writer.met_batcher.queue.get()] == data.metrics_str()


def test_write_callback_invalid_metric_name(initialized_metrics_writer):
    metrics_writer = initialized_metrics_writer
    with pytest.raises(Exception) as e:
        data = Values(type="test")
        metrics_writer.write_callback(data)

    assert "Do not know how to handle type test" in str(e)


@pytest.mark.parametrize(
    "config", [CollectdConfig([Helper.url_node(), Helper.signalfx_statsd_tags_node()])]
)
def test_write_callback_signalfx_statsd_tags(initialized_metrics_writer):
    metrics_writer = initialized_metrics_writer
    data = Values(values=[1], type_instance="metric[key=value].test")
    metrics_writer.write_callback(data)
    assert metrics_writer.met_batcher.queue.qsize() == 1
    metric_str = metrics_writer.met_batcher.queue.get()
    assert " key=value " in metric_str
    assert "type_instance=metric.test" in metric_str


def test_shutdown_call_back(initialized_metrics_writer):
    metrics_writer = initialized_metrics_writer

    for i in range(10):
        metrics_writer.met_buffer.put_pending_batch(["batch_%s" % i])

    metrics_writer.shutdown_callback()

    time.sleep(2)

    assert metrics_writer.met_buffer.empty() is True


def test_received_metrics(initialized_metrics_writer):
    metrics_writer = initialized_metrics_writer
    received_before = metrics_writer.received_metric_count
    data = Values(values=[1, 2], type="test_type_2")
    metrics_writer.write_callback(data)
    received_after = metrics_writer.received_metric_count
    assert received_after == received_before + len(data.values)


def test_register(configured_metrics_writer):
    configured_metrics_writer.register()


class TestReadCallback:
    @pytest.fixture
    def config(self):
        return CollectdConfig(
            [Helper.url_node(), Helper.enable_internal_metrics_node()]
        )

    def test_metrics_values(self, initialized_metrics_writer):
        metrics_writer = initialized_metrics_writer
        with mock.patch.object(metrics_writer.collectd, "Values") as mocked_cls:
            metrics_writer.read_internal_metrics_callback()
            mocked_cls.assert_has_calls(
                [
                    mock.call(
                        plugin=PLUGIN_NAME,
                        type_instance="batch_queue_size",
                        type="gauge",
                        values=[0],
                    ).dispatch(),
                    mock.call(
                        plugin=PLUGIN_NAME,
                        type_instance="received_metrics",
                        type="gauge",
                        values=[metrics_writer.received_metric_count],
                    ).dispatch(),
                    mock.call(
                        plugin=PLUGIN_NAME,
                        type_instance="sent_metrics",
                        type="gauge",
                        values=[metrics_writer.met_sender.sent_metric_count],
                    ).dispatch(),
                    mock.call(
                        plugin=PLUGIN_NAME,
                        type_instance="sent_batches",
                        type="gauge",
                        values=[metrics_writer.met_sender.sent_batch_count],
                    ).dispatch(),
                    mock.call(
                        plugin=PLUGIN_NAME,
                        type_instance="dropped_metrics",
                        type="gauge",
                        values=[metrics_writer.met_buffer.dropped_metric_count],
                    ).dispatch(),
                    mock.call(
                        plugin=PLUGIN_NAME,
                        type_instance="dropped_batches",
                        type="gauge",
                        values=[metrics_writer.met_buffer.dropped_batch_count],
                    ).dispatch(),
                ],
                any_order=True,
            )
