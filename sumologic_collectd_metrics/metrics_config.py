# -*- coding: utf-8 -*-

from metrics_util import validate_non_empty, validate_string_type, validate_positive, \
    validate_non_negative, validate_field


class ConfigOptions(object):
    """
    Config options
    """
    types_db = 'TypesDB'
    url = 'URL'
    # Http header options
    dimension_tags = 'Dimensions'
    meta_tags = 'Metadata'
    source_name = 'SourceName'
    host_name = 'SourceHost'
    source_category = 'SourceCategory'
    # Metrics Batching options
    max_batch_size = 'MaxBatchSize'
    max_batch_interval = 'MaxBatchInterval'
    # Http post request frequency option
    http_post_interval = 'HttpPostInterval'
    # Http retry options
    retry_initial_delay = 'RetryInitialDelay'
    retry_max_attempts = 'RetryMaxAttempts'
    retry_max_delay = 'RetryMaxDelay'
    retry_backoff = 'RetryBackOff'
    retry_jitter_min = 'RetryJitterMin'
    retry_jitter_max = 'RetryJitterMax'
    # Memory option
    max_requests_to_buffer = 'MaxRequestsToBuffer'
    # Content encoding option
    content_encoding = 'ContentEncoding'
    # Static option, not configurable yet. Default is application/vnd.sumologic.carbon2
    content_type = 'ContentType'
    shutdown_max_wait = "ShutdownMaxWait"  # seconds

class MetricsConfig:
    """
    Configuration for sumologic collectd plugin
    """

    _content_encoding_set = frozenset(['deflate', 'gzip', 'none'])

    def __init__(self, collectd):
        """
        Init MetricsConfig with default config
        """
        self.collectd = collectd
        self.conf = self.default_config()
        self.types = {}

        collectd.info('Initialized MetricsConfig with default config %s' % self.conf)

    @staticmethod
    def default_config():
        return {
            ConfigOptions.http_post_interval: 0.1,
            ConfigOptions.max_batch_size: 5000,
            ConfigOptions.max_batch_interval: 1,
            ConfigOptions.retry_initial_delay: 0,
            ConfigOptions.retry_max_attempts: 10,
            ConfigOptions.retry_max_delay: 100,
            ConfigOptions.retry_backoff: 2,
            ConfigOptions.retry_jitter_min: 0,
            ConfigOptions.retry_jitter_max: 10,
            ConfigOptions.max_requests_to_buffer: 1000,
            ConfigOptions.content_encoding: 'deflate',
            ConfigOptions.content_type: 'application/vnd.sumologic.carbon2',
            ConfigOptions.shutdown_max_wait: 5
        }

    def parse_config(self, config):
        """
        Parse the python plugin configurations in collectd.conf
        """

        try:
            for child in config.children:
                if child.key == ConfigOptions.types_db:
                    for v in child.values:
                        self._parse_types(v)
                elif child.key == ConfigOptions.url:
                    url = child.values[0]
                    self.conf[child.key] = url
                    validate_non_empty(url, child.key)
                elif child.key in [ConfigOptions.dimension_tags, ConfigOptions.meta_tags]:
                    self._parse_tags(child)
                elif child.key in [ConfigOptions.source_name, ConfigOptions.host_name,
                                   ConfigOptions.source_category]:
                    s = child.values[0]
                    validate_non_empty(s, child.key)
                    validate_string_type(s, child.key, 'Value', 'Key')
                    self.conf[child.key] = s
                elif child.key == ConfigOptions.http_post_interval:
                    f = float(child.values[0])
                    validate_positive(f, child.key)
                    self.conf[child.key] = f
                elif child.key in [ConfigOptions.max_batch_size, ConfigOptions.max_batch_interval,
                                   ConfigOptions.retry_max_attempts, ConfigOptions.retry_max_delay,
                                   ConfigOptions.retry_backoff,
                                   ConfigOptions.max_requests_to_buffer]:
                    i = int(child.values[0])
                    validate_positive(i, child.key)
                    self.conf[child.key] = i
                elif child.key in [ConfigOptions.retry_initial_delay,
                                   ConfigOptions.retry_jitter_min, ConfigOptions.retry_jitter_max]:
                    i = int(child.values[0])
                    validate_non_negative(i, child.key)
                    self.conf[child.key] = i
                elif child.key == ConfigOptions.content_encoding:
                    s = child.values[0]
                    validate_non_empty(s, child.key)
                    validate_string_type(s, child.key, 'Value', 'Key')
                    content_encoding = s.lower()
                    if content_encoding not in self._content_encoding_set:
                        raise Exception('Unknown ContentEncoding %s specified. ContentEncoding '
                                        'must be deflate, gzip, or none' % s)
                    self.conf[child.key] = content_encoding
                else:
                    self.collectd.warning('Unknown configuration %s, ignored.' % child.key)
        except Exception as e:
            self.collectd.error('Failed to parse configurations due to %s' % str(e))
            raise e

        if ConfigOptions.url not in self.conf:
            raise Exception('Specify %s in collectd.conf.' % ConfigOptions.url)

        if not self.types:
            raise Exception('Specify %s in collectd.conf.' % ConfigOptions.types_db)

        http_post_interval = self.conf[ConfigOptions.http_post_interval]
        max_batch_interval = self.conf[ConfigOptions.max_batch_interval]

        if http_post_interval > max_batch_interval:
            raise Exception('Specify HttpPostInterval %f as float between 0 and '
                            'MaxBatchInterval %d' %(http_post_interval, max_batch_interval))

        retry_jitter_min = self.conf[ConfigOptions.retry_jitter_min]
        retry_jitter_max = self.conf[ConfigOptions.retry_jitter_max]

        if retry_jitter_min > retry_jitter_max:
            raise Exception('Specify RetryJitterMin %d to be less or equal to RetryJitterMax %d' %
                            (retry_jitter_min, retry_jitter_max))

        self.collectd.info('Updated MetricsConfig %s with config file %s ' % (self.conf, config))

    # parse types.db file
    def _parse_types(self, db):

        try:
            f = open(db, 'r')

            for line in f:
                fields = line.split()
                if len(fields) < 2:
                    continue
                type_name = fields[0]
                if type_name[0] == '#':
                    continue
                v = []
                for ds in fields[1:]:
                    ds = ds.rstrip(',')
                    ds_fields = ds.split(':')

                    if len(ds_fields) != 4:
                        self.collectd.warning('Cannot parse data source %s on type %s'
                                         % (ds, type_name))
                        continue
                    v.append(ds_fields)
                self.types[type_name] = v

            f.close()

            self.collectd.info('Parsed types %s with types_db file %s ' % (self.types, db))

        except Exception as e:
            self.collectd.error('Parse types %s failed with %s' %(db, str(e)))
            raise e

    # parse dimension_tags/meta_tags specified in collectd.conf
    def _parse_tags(self, child):
        if len(child.values) % 2 != 0:
            raise Exception('Missing tags key/value in options %s.' % str(child.values))

        for v in child.values:
            validate_field(v, child.key, 'Value', 'Key')

        self.conf[child.key] = zip(*(iter(child.values),) * 2)

        self.collectd.info('Parsed %s tags %s' % (child.key, self.conf[child.key]))
