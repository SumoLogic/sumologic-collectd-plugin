import collectd
from metrics_util import MetricsUtil

class IntrinsicKeys:
    host = "host"
    plugin = "plugin"
    plugin_instance = "plugin_instance"
    type = "type"
    type_instance = "type_instance"
    ds_name = "ds_name"
    ds_type = "ds_type"

class MetricsConverter:
    """
    Coverts collectd data model to carbon 2.0 data model
    """

    # reserved keywords are case-insensitive
    _reserved_keywords = frozenset(['_sourcehost', '_sourcename', '_sourcecategory', '_collectorid',
                          '_collector', '_source', '_sourceid', '_contenttype', '_rawname'])

    @staticmethod
    def convert_to_metrics(data, types):
        """
        Convert data into metrics
        """
        MetricsUtil.validate_type(data, types)

        data_type = types[data.type]

        i = 0

        metrics = []

        for value in data.values:
            ds_name = data_type[i][0]
            ds_type = data_type[i][1]

            dimension_tags = MetricsConverter._gen_dimension_tags(data, ds_name, ds_type)
            meta_tags = MetricsConverter._gen_meta_tags(data)
            metric = MetricsConverter._gen_metric(dimension_tags, meta_tags, value, data.time)

            metrics.append(metric)

            i += 1

        collectd.debug('Converted data %s to metrics %s' %(data, metrics))

        return metrics

    @staticmethod
    def gen_tag(key, value):
        """
        Tag is of form key=value
        """
        MetricsUtil.validate_field(key)
        MetricsUtil.validate_field(value)
        if not key:
            raise Exception('Key for value %s cannot be empty' % value)
        elif key.lower() in MetricsConverter._reserved_keywords:
            raise Exception('Key %s (case-insensitive) must not contain reserved keywords %s' %
                            (key, MetricsConverter._reserved_keywords))
        elif not value:
            return ''
        else:
            return key + '=' + value

    @staticmethod
    def tags_to_str(tags):
        """
        Convert list of tags to a single string
        """
        return ' '.join(MetricsConverter._remove_empty_tags(tags))

    # Generate meta_tags from data
    @staticmethod
    def _gen_meta_tags(data):

        return [MetricsConverter.gen_tag(key, value) for key, value in data.meta.items()]

    @staticmethod
    def _remove_empty_tags(tags):
        return [tag for tag in tags if tag]

    @staticmethod
    def _gen_metric(dimension_tags, meta_tags, value, timestamp):
        """
        Convert (dimension_tags, meta_tags, value, timestamp) to metric string
        """

        if not meta_tags:
            return '%s  %f %i' % (MetricsConverter.tags_to_str(dimension_tags), value, timestamp)

        else:
            return '%s  %s %f %i' % (MetricsConverter.tags_to_str(dimension_tags),
                                     MetricsConverter.tags_to_str(meta_tags), value, timestamp)

    # Generate dimension tags
    @staticmethod
    def _gen_dimension_tags(data, ds_name, ds_type):

        tags = [MetricsConverter.gen_tag(key, getattr(data, key)) for key in
                [IntrinsicKeys.host, IntrinsicKeys.plugin, IntrinsicKeys.plugin_instance,
                 IntrinsicKeys.type, IntrinsicKeys.type_instance]] + \
               [MetricsConverter.gen_tag(IntrinsicKeys.ds_name, ds_name),
                MetricsConverter.gen_tag(IntrinsicKeys.ds_type, ds_type)]

        dimension_tags = MetricsConverter._remove_empty_tags(tags)

        if not dimension_tags:
            raise Exception('Dimension tags for data %s cannot be empty' % data)

        return dimension_tags



