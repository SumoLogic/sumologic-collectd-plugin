# -*- coding: utf-8 -*-

try:
    import Queue as queue
except ImportError:
    import queue


class MetricsBuffer(object):
    """
    Buffer metrics batch that have been submitted by collectd write call back, and yet to be posted
    to remote server. When the buffer is full, the oldest metrics batch will be dropped to make
    space for new metrics batches.
    """

    _processing_queue_size = 10

    def __init__(self, max_requests_to_buffer, collectd):
        """
        Init MetricsBuffer with a pending queue for pending requests
        and a failed queue for failed requests
        """
        self.collectd = collectd
        self.processing_queue = queue.Queue(self._processing_queue_size)
        self.pending_queue = queue.Queue(max_requests_to_buffer)

        # metrics
        self.dropped_batch_count = 0
        self.dropped_metric_count = 0

        collectd.info(
            "Initialized MetricsBuffer with max_requests_to_buffer %s"
            % max_requests_to_buffer
        )

    def get_batch(self):
        """
        If both processing queue and pending queue are empty, return None,
        else if processing queue is empty, return metrics batch from pending queue,
        else, run metrics batch from processing queue.
        """

        if self.processing_queue.empty() and self.pending_queue.empty():
            return None

        if not self.processing_queue.empty():
            return self.processing_queue.get()

        return self.pending_queue.get()

    def put_pending_batch(self, batch):
        """
        Add a batch to pending queue. Blocking if queue is full.
        """

        if self.pending_queue.full():
            batch_to_drop = self.pending_queue.get()
            self.collectd.warning(
                "In memory buffer is full, dropping metrics batch %s" % batch_to_drop
            )
            self._drop_batch(batch_to_drop)

        self.pending_queue.put(batch)

    def put_failed_batch(self, batch):
        """
        Add a batch back to processing queue. If queue is full, drop the metrics batch.
        """

        if self.pending_queue.full():
            self.collectd.warning(
                "Sending metrics batch %s failed. "
                "In memory buffer is full, dropping metrics batch" % batch
            )
            self._drop_batch(batch)
        else:
            self.collectd.warning(
                "Sending metrics batch %s failed. "
                "Put it back to processing queue" % batch
            )
            self.processing_queue.put(batch)

    def _drop_batch(self, batch):
        """
        Drop the supplied batch. This will typically happen due to one of the queues being full.

        This function doesn't do anything other than updating some stats.
        """
        self.dropped_batch_count += 1
        self.dropped_metric_count += len(batch)

    def empty(self):
        return self.processing_queue.empty() and self.pending_queue.empty()

    def size(self):
        return self.processing_queue.qsize() + self.pending_queue.qsize()
