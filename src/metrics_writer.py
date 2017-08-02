import collectd
from metrics_config import MetricsConfig, ConfigOptions
from metrics_buffer import MetricsBuffer
from metrics_converter import MetricsConverter
from metrics_batcher import MetricsBatcher
from metrics_sender import MetricsSender

met_config = MetricsConfig()
met_buffer = None
met_batcher = None
met_sender = None


def config_callback(conf):
    """
    Parse conf file
    """
    met_config.parse_config(conf)

    collectd.info('Parsed configuration %s' % met_config.conf)
    collectd.info('Parsed types %s' % met_config.types)


def init_callback():
    """
    Init MetricsConverter, MetricsBuffer, MetricsBatcher, and MetricsSender
    """

    global met_buffer, met_batcher, met_sender

    met_buffer = MetricsBuffer(met_config.conf[ConfigOptions.max_requests_to_buffer])
    met_batcher = MetricsBatcher(met_config.conf[ConfigOptions.max_batch_size],
                                 met_config.conf[ConfigOptions.flushing_interval],
                                 met_buffer)
    met_sender = MetricsSender(met_config.conf, met_buffer)

    collectd.info('Initialized MetricsBuffer, MetricsConverter, MetricsBatcher, and MetricsSender')


def read_callback(data=None):
    """
    Read callback
    """

    vread = collectd.Values(type='absolute')
    vread.host = 'xyz'
    vread.values = [5]
    vread.meta = {'my_msg_key': 'my_long_message'}
    vread.dispatch()

    collectd.info(" sending out %s" % str(vread))


def write_callback(raw_metrics, data=None):
    """
    Write callback
    """

    metrics = MetricsConverter.convert_to_metrics(raw_metrics, met_config.types)

    for metric in metrics:
        met_batcher.push_item(metric)


collectd.register_config(config_callback)
collectd.register_init(init_callback)
collectd.register_read(read_callback)
collectd.register_write(write_callback)
