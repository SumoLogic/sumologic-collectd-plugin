import collectd
import Queue


class MetricsBuffer:
    """
    Buffer pending requests and retry on failed requests. Upon buffer full, dropping oldest request.
    """

    def __init__(self, max_requests_to_buffer):
        """
        Init MetricsBuffer with a pending queue for pending requests
        and a failed queue for failed requests
        """

        self.processing_queue = Queue.Queue(1)
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
        elif self.processing_queue.empty():
            return self.pending_queue.get_nowait()
        else:
            return self.processing_queue.get_nowait()

    def put_pending_batch(self, batch):
        """
        Add a batch to pending queue. Blocking if queue is full.
        """

        self.pending_queue.put(batch)
        self.pending_queue.task_done()

    def put_failed_batch(self, batch):
        """
        Add a batch back to processing queue. If queue is full, drop the metrics batch.
        """

        assert self.processing_queue.empty()

        if self.pending_queue.full():
            collectd.warning('MetricsBuffer: sending metrics batch %s failed. '
                             'In memory buffer is full. Dropping metrics batch %s' % batch)
        else:
            collectd.warning('MetricsBuffer: sending metrics batch %s failed. '
                             'Put it back to processing queue' % batch)
            self.processing_queue.put_nowait(batch)
            self.pending_queue.task_done()
