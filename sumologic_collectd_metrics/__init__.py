try:  # pragma: no cover
    import collectd

    COLLECTD_PRESENT = True
except (ImportError, AttributeError):  # pragma: no cover
    COLLECTD_PRESENT = False

from .metrics_writer import MetricsWriter  # pragma: no cover


def config_callback(conf):  # pragma: no cover
    met_writer.parse_config(conf)
    met_writer.register()


if COLLECTD_PRESENT:  # pragma: no cover
    met_writer = MetricsWriter(collectd)
    collectd.register_config(config_callback)
