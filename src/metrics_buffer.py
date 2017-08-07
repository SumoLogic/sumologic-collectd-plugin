import collectd
import Queue


class MetricsBuffer:
    """
    Buffer metrics batch that have been submitted by collectd write call back, and yet to be posted
    to remote server. When the buffer is full, the oldest metrics batch will be dropped to make
    space for new metrics batches.
    """

    _processing_queue_size = 10

    def __init__(self, max_requests_to_buffer):
        """
        Init MetricsBuffer with a pending queue for pending requests
        and a failed queue for failed requests
        """

        self.processing_queue = Queue.Queue(self._processing_queue_size)
        self.pending_queue = Queue.Queue(max_requests_to_buffer)

        collectd.info('Initialized MetricsBuffer with max_requests_to_buffer %s' %
                      max_requests_to_buffer)

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
        else:
            return self.pending_queue.get()

    def put_pending_batch(self, batch):
        """
        Add a batch to pending queue. Blocking if queue is full.
        """

        if self.pending_queue.full():
            batch_to_drop = self.pending_queue.get()
            collectd.warning('In memory buffer is full, dropping metrics batch %s' % batch_to_drop)

        self.pending_queue.put(batch)

    def put_failed_batch(self, batch):
        """
        Add a batch back to processing queue. If queue is full, drop the metrics batch.
        """

        if self.pending_queue.full():
            collectd.warning('Sending metrics batch %s failed. '
                             'In memory buffer is full, dropping metrics batch' % batch)
        else:
            collectd.warning('Sending metrics batch %s failed. '
                             'Put it back to processing queue' % batch)
            self.processing_queue.put(batch)
