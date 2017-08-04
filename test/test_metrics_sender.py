import os
cwd = os.getcwd()
import sys
sys.path.append(cwd + '/src')

import pytest
from metrics_config import MetricsConfig, ConfigOptions
from metrics_sender import MetricsSender
from collectd.collectd_config import CollectdConfig, ConfigNode
from collectd.helper import Helper


