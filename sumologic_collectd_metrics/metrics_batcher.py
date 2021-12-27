# -*- coding: utf-8 -*-

try:
    import Queue as queue
except ImportError:
    import queue

import threading

from .timer import Timer


class MetricsBatcher(Timer):
    """
    Groups metrics in to batches based on max_batch_size and max_batch_interval
    """

    def __init__(self, max_batch_size, max_batch_interval, met_buffer, collectd):
        """
        Init MetricsBatcher with max_batch_size, max_batch_interval, and met_buffer
        """

        self.collectd = collectd
        Timer.__init__(self, max_batch_interval, self.flush)
        # initiate max_batch_size and max_batch_interval
        self.max_batch_size = max_batch_size
        self.max_batch_interval = max_batch_interval

        # init batching queue to 2 * max_batch_size so that producer can still write while flushing
        self.queue = queue.Queue(2 * max_batch_size)

        # init lock for flushing
        self.flushing_lock = threading.Lock()
        self.metrics_buffer = met_buffer

        # start timer
        self.start_timer()

        collectd.info(
            "Initialized MetricsBatcher with max_batch_size %s, max_batch_interval %s"
            % (max_batch_size, max_batch_interval)
        )

    def push_item(self, item):
        """
        Add a new metric to the batching queue
        """

        self.queue.put(item)
        if self._batch_full():
            self.flush()

    def flush(self):

        if self.queue.empty():
            self.collectd.debug("queue is empty")
            return
        if self.flushing_lock.acquire(False):  # pylint: disable=R1732
            batch = self._pop_batch()
            self.collectd.debug("flushing metrics with batch size %d" % len(batch))
            self.metrics_buffer.put_pending_batch(batch)
            self.reset_timer()
            self.flushing_lock.release()

    # Test whether we have enough metrics in batching queue to form a full batch
    def _batch_full(self):

        return self.queue.qsize() >= self.max_batch_size

    # Calculate the maximum batch we can group in to one batch
    def _batch_size(self):

        size = self.max_batch_size if self._batch_full() else self.queue.qsize()
        return size

    # Pops the maximum batch we can group from batching queue
    def _pop_batch(self):

        batch = []

        for _ in range(self._batch_size()):
            batch.append(self.queue.get())

        return batch
