try:
    import collectd
    collectd_present = True  # pragma: no cover
except (ImportError, AttributeError):
    collectd_present = False

from . metrics_writer import MetricsWriter


def config_callback(conf):  # pragma: no cover
    met_writer.parse_config(conf)
    met_writer.register()

if collectd_present:  # pragma: no cover
    met_writer = MetricsWriter(collectd)
    collectd.register_config(config_callback)