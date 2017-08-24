try:  # pragma: no cover
    import collectd
    collectd_present = True
except (ImportError, AttributeError):  # pragma: no cover
    collectd_present = False

from . metrics_writer import MetricsWriter  # pragma: no cover


def config_callback(conf):  # pragma: no cover
    met_writer.parse_config(conf)
    met_writer.register()

if collectd_present:  # pragma: no cover
    met_writer = MetricsWriter(collectd)
    collectd.register_config(config_callback)