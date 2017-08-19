# -*- coding: utf-8 -*-

import time
from metrics_config import MetricsConfig, ConfigOptions
from metrics_buffer import MetricsBuffer
from metrics_converter import convert_to_metrics
from metrics_batcher import MetricsBatcher
from metrics_sender import MetricsSender


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

    def parse_config(self, conf):
        """
        Parse conf file
        """
        self.met_config = MetricsConfig(self.collectd)
        self.met_config.parse_config(conf)

        self.collectd.info('Parsed configuration %s' % self.met_config.conf)
        self.collectd.info('Parsed types %s' % self.met_config.types)

    def init_callback(self):
        """
        Init MetricsBuffer, MetricsBatcher, and MetricsSender
        """

        self.met_buffer = MetricsBuffer(self.met_config.conf[ConfigOptions.max_requests_to_buffer],
                                   self.collectd)
        self.met_batcher = MetricsBatcher(self.met_config.conf[ConfigOptions.max_batch_size],
                                     self.met_config.conf[ConfigOptions.max_batch_interval],
                                     self.met_buffer, self.collectd)
        self.met_sender = MetricsSender(self.met_config.conf, self.met_buffer, self.collectd)

        self.collectd.info('Initialized MetricsBuffer, MetricsBatcher, and MetricsSender')

    def write_callback(self, raw_data, data=None):
        """
        Write callback
        """

        metrics = convert_to_metrics(raw_data, self.met_config.types)

        self.collectd.debug('Converted data %s to metrics %s' % (raw_data, metrics))

        for metric in metrics:
            self.met_batcher.push_item(metric)

    def shutdown_callback(self):
        """
        Shutdown callback. Flushes in memory metrics batches. Default, times out at 5 seconds.
        """

        self.collectd.info('Received shutdown signal, start flushing in memory metrics batches.')

        now = time.time()
        stop = now + self.met_config.conf[ConfigOptions.shutdown_max_wait]
        self.met_batcher.cancel_timer()
        self.met_batcher.flush()
        flush_interval = 0.1  # 100 ms
        # Increase frequency for scheduling http requests
        self.met_sender.interval = flush_interval
        while time.time() < stop and (not self.met_buffer.empty()):
            time.sleep(flush_interval)

        self.collectd.info('Flushing complete. There are %d metrics batches left.' %
                           (self.met_buffer.pending_queue.qsize() +
                           self.met_buffer.processing_queue.qsize()))

    def register(self):
        """
        Register callbacks for init, write, and shutdown.
        """
        self.collectd.register_init(self.init_callback)
        self.collectd.register_write(self.write_callback)
        self.collectd.register_shutdown(self.shutdown_callback)