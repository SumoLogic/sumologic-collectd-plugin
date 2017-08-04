import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/src')
import pytest
from metrics_converter import MetricsConverter
from metrics_buffer import MetricsBuffer
from collectd.values import Values
from collectd.helper import Helper


def test_get_batch_processing_queue_empty():
    met_buffer = MetricsBuffer(10)
    pass


def test_get_batch_pending_queue_empty():
    pass


def test_get_batch_both_queue_empty():
    pass


def test_get_batch_both_queue_nonempty():
    pass


def test_put_pending_batch_queue_full():
    size = 10
    met_buffer = MetricsBuffer(size)
    for i in range(10):
        met_buffer.put_pending_batch(['batch_%s' % i])

    assert met_buffer.pending_queue.qsize() == 10


def test_put_pending_batch_queue_not_full():
    size = 10
    met_buffer = MetricsBuffer(size)
    for i in range(10):
        met_buffer.put_pending_batch(['batch_%s' % i])

    assert met_buffer.pending_queue.qsize() == 10


def test_put_failed_batch_queue_full():
    pass


def test_put_failed_batch_queue_not_full():
    pass