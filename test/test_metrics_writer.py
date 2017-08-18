import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/src')

import time
import metrics_writer
from metrics_config import ConfigOptions
from collectd.collectd_config import CollectdConfig
from collectd.values import Values
from collectd.helper import Helper


def test_config_callback():
    config = CollectdConfig([Helper.url_node(), Helper.types_db_node()])
    metrics_writer.config_callback(config)

    metrics_writer.met_config.conf[ConfigOptions.url] = Helper.url


def test_init_callback():
    metrics_writer.init_callback()
    assert metrics_writer.met_buffer is not None
    assert metrics_writer.met_batcher is not None
    assert metrics_writer.met_sender is not None
    metrics_writer.met_batcher.cancel_timer()
    metrics_writer.met_sender.cancel_timer()


def test_write_callback():
    d = Values()
    metrics_writer.write_callback(d)
    assert metrics_writer.met_batcher.queue.qsize() == 1
    assert [metrics_writer.met_batcher.queue.get()] == d.metrics_str()


def test_shutdown_call_back():
    config = CollectdConfig([Helper.url_node(), Helper.types_db_node()])
    metrics_writer.config_callback(config)
    metrics_writer.init_callback()

    for i in range(10):
        metrics_writer.met_buffer.put_pending_batch(['batch_%s' % i])

    metrics_writer.shutdown_callback()

    time.sleep(2)

    assert metrics_writer.met_buffer.empty() == True

