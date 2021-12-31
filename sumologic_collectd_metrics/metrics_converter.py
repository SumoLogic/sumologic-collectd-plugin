# -*- coding: utf-8 -*-
# pylint: disable=logging-not-lazy

import math
import re

from .metrics_util import sanitize_field

# Log to collectd if present, otherwise to a default logger. This is so we don't need to manually
# pass the right logger to every function individually.
try:  # pragma: no cover
    import collectd as logger
except (ImportError, AttributeError):  # pragma: no cover
    import logging

    logger = logging.getLogger(__name__)


class IntrinsicKeys(object):
    host = "host"
    plugin = "plugin"
    plugin_instance = "plugin_instance"
    type = "type"
    type_instance = "type_instance"
    ds_name = "ds_name"
    ds_type = "ds_type"
    metric = "metric"


# reserved keywords are case-insensitive
_reserved_keywords = frozenset(
    [
        "_sourcehost",
        "_sourcename",
        "_sourcecategory",
        "_collectorid",
        "_collector",
        "_source",
        "_sourceid",
        "_contenttype",
        "_rawname",
    ]
)


def gen_tag(key, value):
    """
    Tag is of form key=value
    """
    key = sanitize_field(key)
    value = sanitize_field(value)
    if not key:
        raise Exception("Key for value %s cannot be empty" % value)

    if key.lower() in _reserved_keywords:
        raise Exception(
            "Key %s (case-insensitive) must not contain reserved keywords %s"
            % (key, _reserved_keywords)
        )

    if not value:
        return ""

    return key + "=" + value


def _remove_empty_tags(tags):
    return [tag for tag in tags if tag]


def tags_to_str(tags, sep=" "):
    """
    Convert list of tags to a single string
    """
    return sep.join(_remove_empty_tags(tags))


# Generate meta_tags from data
def _gen_meta_tags(data):

    return [gen_tag(key, value) for key, value in data.meta.items()]


def _gen_metric(dimension_tags, meta_tags, value, timestamp):
    """
    Convert (dimension_tags, meta_tags, value, timestamp) to metric string
    """

    if not meta_tags:
        return "%s  %f %i" % (tags_to_str(dimension_tags), value, timestamp)

    return "%s  %s %f %i" % (
        tags_to_str(dimension_tags),
        tags_to_str(meta_tags),
        value,
        timestamp,
    )


# Generate dimension tags
def _gen_dimension_tags(data, ds_name, ds_type):

    tags = [
        gen_tag(key, getattr(data, key))
        for key in [
            IntrinsicKeys.host,
            IntrinsicKeys.plugin,
            IntrinsicKeys.plugin_instance,
            IntrinsicKeys.type,
            IntrinsicKeys.type_instance,
        ]
    ] + [
        gen_tag(IntrinsicKeys.ds_name, ds_name),
        gen_tag(IntrinsicKeys.ds_type, ds_type),
    ]

    dimension_tags = _remove_empty_tags(tags)

    return dimension_tags


def _gen_metric_dimension(data, sep):
    """
    Generates metric dimension and returns it as one-element list
    """
    if sep is None:
        return []

    return [
        gen_tag(
            IntrinsicKeys.metric,
            sep.join(v for v in (data.type, data.type_instance) if v),
        )
    ]


def convert_to_metrics(data, data_set, sep):
    """
    Convert data into metrics
    """
    metrics = []
    metric_dimension = _gen_metric_dimension(data, sep)
    meta_tags = _gen_meta_tags(data)

    for (value, data_type) in zip(data.values, data_set):
        if math.isnan(value):
            continue

        ds_name = data_type[0]
        ds_type = data_type[1]

        dimension_tags = _gen_dimension_tags(data, ds_name, ds_type) + metric_dimension
        metric = _gen_metric(dimension_tags, meta_tags, value, data.time)

        metrics.append(metric)

    return metrics


def process_signalfx_statsd_tags(data):
    """
    Process statsd tags embedded in the metric name within the supplied raw data. This function
    modifies the raw data in-place.

    :param data:
    :type data: collectd.Values
    :return:
    :rtype: None
    """
    cleaned_type_instance, new_metadata = parse_statsd_signalfx_metric_name(
        data.type_instance
    )
    data.type_instance = cleaned_type_instance
    data.meta.update(new_metadata)


def parse_statsd_signalfx_metric_name(metric_name):
    """
    Parse the metric name and extract metadata from it according to SignalFx' custom extension to
    the StatsD protocol.
    See: https://docs.signalfx.com/en/latest/integrations/agent/monitors/collectd-statsd.html#adding-dimensions-to-statsd-metrics

    :param metric_name: The metric name
    :type metric_name: str
    :return: A pair consisting of the modified metric name without the metadata, and a dict of
    extracted metadata.
    :rtype: (str, dict)
    """  # pylint: disable=line-too-long
    matcher = re.compile(r"\[([^\]]+)\]")
    matches = matcher.findall(metric_name)
    if len(matches) > 1:
        # if we find more than one metadata segment, something is probably wrong, and we should
        # ignore it
        logger.warning(
            "Found more than one metadata segment in metric name `%s`. "
            "Ignoring all segments." % metric_name
        )
        return metric_name, {}

    if len(matches) == 0:
        # if we find no segments, we have nothing to do
        return metric_name, {}

    metadata = {}
    tag_string = matches[0]
    key_value_strings = tag_string.split(",")
    for key_value_string in key_value_strings:
        key_value_string = key_value_string.strip()
        parts = [p.strip() for p in key_value_string.split("=")]
        if len(parts) != 2:  # ignore malformed entries, but parse as much as we can
            logger.warning(
                "Invalid key=value pair `%s` in metric name `%s`, ignoring it"
                % (key_value_string, metric_name)
            )
            continue
        key, value = parts
        if key == "":
            logger.warning(
                "Empty keys aren't supported, ignoring key=value pair `%s` in metric name `%s`"
                % (key_value_string, metric_name)
            )
            continue
        if key in metadata:
            logger.warning(
                "Key `%s` is defined multiple times in metric name `%s`, ignoring subsequent values"
                % (key, metric_name)
            )
            continue
        metadata[key] = value
    if len(metadata) > 0:
        # remove tags from the key, but only if we extracted any metadata successfully
        # otherwise, we should treat the data as invalid and not modify the name
        cleaned_key = matcher.sub("", metric_name)
    else:
        return metric_name, {}
    return cleaned_key, metadata
