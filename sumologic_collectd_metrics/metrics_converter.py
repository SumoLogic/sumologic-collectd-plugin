# -*- coding: utf-8 -*-

import math

from .metrics_util import sanitize_field


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
_reserved_keywords = frozenset(['_sourcehost', '_sourcename', '_sourcecategory', '_collectorid',
                                '_collector', '_source', '_sourceid', '_contenttype', '_rawname'])


def gen_tag(key, value):
    """
    Tag is of form key=value
    """
    key = sanitize_field(key)
    value = sanitize_field(value)
    if not key:
        raise Exception('Key for value %s cannot be empty' % value)

    if key.lower() in _reserved_keywords:
        raise Exception('Key %s (case-insensitive) must not contain reserved keywords %s' %
                        (key, _reserved_keywords))

    if not value:
        return ''

    return key + '=' + value


def _remove_empty_tags(tags):
    return [tag for tag in tags if tag]


def tags_to_str(tags, sep=' '):
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
        return '%s  %f %i' % (tags_to_str(dimension_tags), value, timestamp)


    return '%s  %s %f %i' % (tags_to_str(dimension_tags),
                             tags_to_str(meta_tags), value, timestamp)


# Generate dimension tags
def _gen_dimension_tags(data, ds_name, ds_type):

    tags = [gen_tag(key, getattr(data, key)) for key in
            [IntrinsicKeys.host, IntrinsicKeys.plugin, IntrinsicKeys.plugin_instance,
                IntrinsicKeys.type, IntrinsicKeys.type_instance]] + \
            [gen_tag(IntrinsicKeys.ds_name, ds_name),
            gen_tag(IntrinsicKeys.ds_type, ds_type)]

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
            sep.join(v for v in (data.type, data.type_instance) if v)
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
