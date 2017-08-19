# -*- coding: utf-8 -*-

import collectd
import time
from metrics_config import MetricsConfig, ConfigOptions
from metrics_buffer import MetricsBuffer
from metrics_converter import convert_to_metrics
from metrics_batcher import MetricsBatcher
from metrics_sender import MetricsSender

met_config = MetricsConfig(collectd)
met_buffer = None
met_batcher = None
met_sender = None


def config_callback(conf):
    """
    Parse conf file
    """
    met_config.parse_config(conf)

    collectd.info('Parsed configuration %s' % met_config.conf)
    collectd.info('Parsed types %s' % met_config.types)


def init_callback():
    """
    Init MetricsBuffer, MetricsBatcher, and MetricsSender
    """

    global met_buffer, met_batcher, met_sender

    met_buffer = MetricsBuffer(met_config.conf[ConfigOptions.max_requests_to_buffer], collectd)
    met_batcher = MetricsBatcher(met_config.conf[ConfigOptions.max_batch_size],
                                 met_config.conf[ConfigOptions.max_batch_interval],
                                 met_buffer, collectd)
    met_sender = MetricsSender(met_config.conf, met_buffer, collectd)

    collectd.info('Initialized MetricsBuffer, MetricsBatcher, and MetricsSender')


def write_callback(raw_data, data=None):
    """
    Write callback
    """

    metrics = convert_to_metrics(raw_data, met_config.types)

    collectd.debug('Converted data %s to metrics %s' % (raw_data, metrics))

    for metric in metrics:
        met_batcher.push_item(metric)


def shutdown_callback():
    """
    Shutdown callback. Flushes in memory metrics batches. Default, times out at 5 seconds.
    """
    now = time.time()
    stop = now + met_config.conf[ConfigOptions.shutdown_max_wait]
    met_batcher.cancel_timer()
    met_batcher.flush()
    flush_interval = 0.1  # 100 ms
    # Increase frequency for scheduling http requests
    met_sender.interval = flush_interval
    while time.time() < stop and (not met_buffer.empty()):
        time.sleep(flush_interval)


collectd.register_config(config_callback)
collectd.register_init(init_callback)
collectd.register_write(write_callback)
collectd.register_shutdown(shutdown_callback)
