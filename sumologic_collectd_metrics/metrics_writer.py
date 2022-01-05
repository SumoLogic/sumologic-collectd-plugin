# -*- coding: utf-8 -*-

import time

from .metrics_batcher import MetricsBatcher
from .metrics_buffer import MetricsBuffer
from .metrics_config import ConfigOptions, MetricsConfig
from .metrics_converter import convert_to_metrics, process_signalfx_statsd_tags
from .metrics_sender import MetricsSender

PLUGIN_NAME = "sumologic_collectd_metrics"


class MetricsWriter(object):
    def __init__(self, collectd):
        """
        Since the collectd module is only available when the plugin is running
        in collectd's python process, we use some dependency injection here.
        """
        self.collectd = collectd
        self.met_config = None
        self.config = None
        self.met_buffer = None
        self.met_batcher = None
        self.met_sender = None

        # metrics
        self.received_metric_count = 0

    def parse_config(self, conf):
        """
        Parse conf file
        """
        self.met_config = MetricsConfig(self.collectd)
        self.met_config.parse_config(conf)

        self.collectd.info("Parsed configuration %s" % self.met_config.conf)

    def init_callback(self):
        """
        Init MetricsBuffer, MetricsBatcher, and MetricsSender
        """

        self.met_buffer = MetricsBuffer(
            self.met_config.conf[ConfigOptions.max_requests_to_buffer], self.collectd
        )
        self.met_batcher = MetricsBatcher(
            self.met_config.conf[ConfigOptions.max_batch_size],
            self.met_config.conf[ConfigOptions.max_batch_interval],
            self.met_buffer,
            self.collectd,
        )
        self.met_sender = MetricsSender(
            self.met_config.conf, self.met_buffer, self.collectd
        )

        self.collectd.info(
            "Initialized MetricsBuffer, MetricsBatcher, and MetricsSender"
        )

    def write_callback(self, raw_data, _=None):
        """
        Write callback
        """

        try:
            data_set = self.collectd.get_dataset(raw_data.type)
        except TypeError:
            raise Exception(  # pylint: disable=W0707
                "Do not know how to handle type %s" % raw_data.type
            )
        if self.met_config.conf[ConfigOptions.signalfx_statsd_tags]:
            process_signalfx_statsd_tags(raw_data)

        metrics = convert_to_metrics(
            raw_data,
            data_set,
            self.met_config.conf[ConfigOptions.metric_dimension_separator],
        )

        self.collectd.debug("Converted data %s to metrics %s" % (raw_data, metrics))

        for metric in metrics:
            self.met_batcher.push_item(metric)
        self.received_metric_count += len(metrics)

    def read_internal_metrics_callback(self):
        """
        Dispatch metrics describing the plugin's state.
        """
        values = [
            self.collectd.Values(
                plugin=PLUGIN_NAME,
                type_instance="batch_queue_size",
                type="gauge",
                values=[self.met_buffer.size()],
            ),
            self.collectd.Values(
                plugin=PLUGIN_NAME,
                type_instance="received_metrics",
                type="gauge",
                values=[self.received_metric_count],
            ),
            self.collectd.Values(
                plugin=PLUGIN_NAME,
                type_instance="sent_batches",
                type="gauge",
                values=[self.met_sender.sent_batch_count],
            ),
            self.collectd.Values(
                plugin=PLUGIN_NAME,
                type_instance="sent_metrics",
                type="gauge",
                values=[self.met_sender.sent_metric_count],
            ),
            self.collectd.Values(
                plugin=PLUGIN_NAME,
                type_instance="dropped_batches",
                type="gauge",
                values=[self.met_buffer.dropped_batch_count],
            ),
            self.collectd.Values(
                plugin=PLUGIN_NAME,
                type_instance="dropped_metrics",
                type="gauge",
                values=[self.met_buffer.dropped_metric_count],
            ),
        ]

        for value in values:
            value.dispatch()

    def shutdown_callback(self):
        """
        Shutdown callback. Flushes in memory metrics batches. Default, times out at 5 seconds.
        """

        self.collectd.info(
            "Received shutdown signal, start flushing in memory metrics batches."
        )

        now = time.time()
        stop = now + self.met_config.conf[ConfigOptions.shutdown_max_wait]
        self.met_batcher.cancel_timer()
        self.met_batcher.flush()
        flush_interval = 0.1  # 100 ms
        # Increase frequency for scheduling http requests
        self.met_sender.interval = flush_interval
        while time.time() < stop and (not self.met_buffer.empty()):
            time.sleep(flush_interval)

        self.collectd.info(
            "Flushing complete. There are %d metrics batches left."
            % (
                self.met_buffer.pending_queue.qsize()
                + self.met_buffer.processing_queue.qsize()
            )
        )

    def register(self):
        """
        Register callbacks for collectd.
        """
        self.collectd.register_init(self.init_callback)
        self.collectd.register_write(self.write_callback)
        self.collectd.register_shutdown(self.shutdown_callback)
        if self.met_config.conf[ConfigOptions.enable_internal_metrics]:
            self.collectd.register_read(self.read_internal_metrics_callback)
