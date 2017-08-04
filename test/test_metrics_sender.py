import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/src')

import pytest
import requests
import time
from metrics_sender import MetricsSender
from metrics_buffer import MetricsBuffer
from collectd.helper import Helper


@pytest.fixture(scope="function", autouse=True)
def reset_response_decider_and_fake_server():
    requests.post_response_decider.reset()
    requests.mock_server.reset()
    requests.mock_response.reset()


def test_post_normal():
    met_buffer = MetricsBuffer(10)
    helper = Helper()

    for i in range(10):
        met_buffer.put_pending_batch(['batch_%s' % i])

    met_sender = MetricsSender(helper.conf, met_buffer)

    time.sleep(1)

    met_sender.cancel_timer()







