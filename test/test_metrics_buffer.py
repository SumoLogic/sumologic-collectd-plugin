from collectd import Helper


def test_get_batch_processing_queue_empty():
    met_buffer = Helper.default_buffer()
    for i in range(10):
        met_buffer.put_pending_batch(['batch_%s' % i])

    for i in range(10):
        assert met_buffer.get_batch() == ['batch_%s' % i]


def test_get_batch_pending_queue_empty():
    met_buffer = Helper.default_buffer()
    met_buffer.processing_queue.put(['batch_0'])

    assert met_buffer.get_batch() == ['batch_0']
    assert met_buffer.get_batch() is None


def test_get_batch_both_queue_empty():
    met_buffer = Helper.default_buffer()
    assert met_buffer.get_batch() is None


def test_get_batch_both_queue_nonempty():
    met_buffer = Helper.default_buffer()
    for i in range(10):
        met_buffer.put_pending_batch(['batch_%s' % i])
    met_buffer.processing_queue.put(['batch_0'])

    assert met_buffer.get_batch() == ['batch_0']
    for i in range(10):
        assert met_buffer.pending_queue.get() == ['batch_%s' % i]


def test_put_pending_batch_queue_full():
    met_buffer = Helper.default_buffer()
    for i in range(20):
        met_buffer.put_pending_batch(['batch_%s' % i])

    for i in range(10, 20):
        assert met_buffer.pending_queue.get() == ['batch_%s' % i]


def test_put_pending_batch_queue_not_full():
    met_buffer = Helper.default_buffer()
    for i in range(10):
        met_buffer.put_pending_batch(['batch_%s' % i])

    for i in range(10):
        assert met_buffer.pending_queue.get() == ['batch_%s' % i]


def test_put_failed_batch_queue_full():
    met_buffer = Helper.default_buffer()
    for i in range(10):
        met_buffer.put_pending_batch(['batch_%s' % i])
    met_buffer.put_failed_batch(['batch_%s' % 11])

    assert met_buffer.processing_queue.empty()
    for i in range(10):
        assert met_buffer.pending_queue.get() == ['batch_%s' % i]


def test_put_failed_batch_queue_not_full():
    met_buffer = Helper.default_buffer()
    for i in range(5):
        met_buffer.put_pending_batch(['batch_%s' % i])
    met_buffer.put_failed_batch(['batch_%s' % 11])

    assert met_buffer.processing_queue.get() == ['batch_%s' % 11]
    for i in range(5):
        assert met_buffer.pending_queue.get() == ['batch_%s' % i]
