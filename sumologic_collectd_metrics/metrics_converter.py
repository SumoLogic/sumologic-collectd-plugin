# -*- coding: utf-8 -*-

from metrics_util import validate_field, validate_type
import math


class IntrinsicKeys(object):
    host = "host"
    plugin = "plugin"
    plugin_instance = "plugin_instance"
    type = "type"
    type_instance = "type_instance"
    ds_name = "ds_name"
    ds_type = "ds_type"


# reserved keywords are case-insensitive
_reserved_keywords = frozenset(['_sourcehost', '_sourcename', '_sourcecategory', '_collectorid',
                                '_collector', '_source', '_sourceid', '_contenttype', '_rawname'])


def gen_tag(key, value):
        """
        Tag is of form key=value
        """
        validate_field(key, value, 'Key', 'Value')
        validate_field(value, key, 'Value', 'Key')
        if not key:
            raise Exception('Key for value %s cannot be empty' % value)
        elif key.lower() in _reserved_keywords:
            raise Exception('Key %s (case-insensitive) must not contain reserved keywords %s' %
                            (key, _reserved_keywords))
        elif not value:
            return ''
        else:
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

        else:
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


def convert_to_metrics(data, types):
    """
    Convert data into metrics
    """
    validate_type(data, types)

    metrics = []

    for (value, data_type) in zip(data.values, types[data.type]):
        if (math.isnan(value)):
            continue;
        ds_name = data_type[0]
        ds_type = data_type[1]

        dimension_tags = _gen_dimension_tags(data, ds_name, ds_type)
        meta_tags = _gen_meta_tags(data)
        metric = _gen_metric(dimension_tags, meta_tags, value, data.time)

        metrics.append(metric)

    return metrics
