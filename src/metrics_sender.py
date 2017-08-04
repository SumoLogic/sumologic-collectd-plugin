import collectd
import requests
import zlib
from retry.api import retry_call
from metrics_config import ConfigOptions
from metrics_util import MetricsUtil, RecoverableException
from metrics_converter import MetricsConverter
from timer import Timer


class HeaderKeys:
    """
    Http header keys
    """

    content_type = 'Content-Type'
    content_encoding = 'Content-Encoding'
    x_sumo_source = 'X-Sumo-Name'
    x_sumo_host = 'X-Sumo-Host'
    x_sumo_category = 'X-Sumo-Category'
    x_sumo_dimensions = 'X-Sumo-Dimensions'
    x_sumo_metadata = 'X-Sumo-Metadata'


class MetricsSender(Timer):
    """
    Fetches metrics batch from MetricsBuffer and post the http request with error handling
    """

    # List of recoverable 4xx http errors. List of http error codes listed here
    # https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
    _recoverable_http_client_errs = frozenset([404, 408, 429])
    _recoverable_http_server_errs = frozenset([500, 502, 503, 504, 506, 507, 508, 510, 511])

    def __init__(self, conf, met_buf):
        """
        Init MetricsSender with conf and met_buf
        """

        Timer.__init__(self, conf[ConfigOptions.http_post_interval], self._request_scheduler)

        self.conf = conf
        self.buffer = met_buf
        self.http_headers = self._build_header()
        self.timer = None
        # start timer
        self.start_timer()

    # Scheduler to send metrics batch via https
    def _request_scheduler(self):

        batch = self.buffer.get_batch()
        try:
            if batch is not None:
                self._send_request_with_retries(batch)
        except RecoverableException as e:
            collectd.warning('Sending metrics batch %s failed after all retries due to %s. '
                             'Put metrics batch into failed metrics buffer.' % (batch, e.message))
            self.buffer.put_failed_batch(batch)
        except Exception as e:
            collectd.warning('Sending metrics batch %s encountered unrecoverable exception %s.'
                             % (batch, e.message))
            raise e

    # Send metrics batch via https with error handling
    # Exceptions defined in https://github.com/requests/requests/blob/master/requests/exceptions.py
    def _send_request(self, headers, body):

        try:
            collectd.debug('Sending https request with headers %s, body %s' %(headers, body))

            response = requests.post(self.conf[ConfigOptions.url],
                                     data=MetricsSender._encode_body(body), headers=headers)

            collectd.info('Sent https request with batch size %d got response code %s' %
                          (len(body), response.status_code))
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in self._recoverable_http_client_errs:
                MetricsUtil.fail_with_recoverable_exception('Client side HTTP error', body, e)
            elif e.response.status_code in self._recoverable_http_server_errs:
                MetricsUtil.fail_with_recoverable_exception('Server side HTTP error', body, e)
            else:
                MetricsUtil.fail_with_unrecoverable_exception('An HTTP error occurred', body, e)
        except requests.exceptions.ConnectionError as e:
            MetricsUtil.fail_with_recoverable_exception('A Connection error occurred', body, e)
        except requests.exceptions.Timeout as e:
            MetricsUtil.fail_with_recoverable_exception('The request timed out', body, e)
        except requests.exceptions.TooManyRedirects as e:
            MetricsUtil.fail_with_recoverable_exception('Too many redirects', body, e)
        except requests.exceptions.URLRequired as e:
            MetricsUtil.fail_with_unrecoverable_exception(
                'A valid URL is required to make a request', body, e)
        except requests.exceptions.MissingSchema as e:
            MetricsUtil.fail_with_unrecoverable_exception(
                'The URL schema (e.g. http or https) is missing', body, e)
        except requests.exceptions.InvalidSchema as e:
            MetricsUtil.fail_with_unrecoverable_exception('See schemas in defaults.py', body, e)
        except requests.exceptions.InvalidURL as e:
            MetricsUtil.fail_with_unrecoverable_exception('The URL provided was invalid', body, e)
        except requests.exceptions.ChunkedEncodingError as e:
            MetricsUtil.fail_with_unrecoverable_exception(
                'The server declared chunked encoding but sent an invalid chunk', body, e)
        except requests.exceptions.ContentDecodingError as e:
            MetricsUtil.fail_with_unrecoverable_exception('Failed to decode response', body, e)
        except requests.exceptions.StreamConsumedError as e:
            MetricsUtil.fail_with_unrecoverable_exception(
                'The content for this response was already consumed', body, e)
        except requests.exceptions.RetryError as e:
            MetricsUtil.fail_with_unrecoverable_exception('Custom retries logic failed', body, e)
        except Exception as e:
            MetricsUtil.fail_with_unrecoverable_exception('unknown exception', body, e)

    # Send http request with retries
    def _send_request_with_retries(self, batch):

        retry_call(self._send_request, fargs=[self.http_headers, batch],
                   exceptions=RecoverableException,
                   tries=self.conf[ConfigOptions.retry_max_attempts],
                   delay=self.conf[ConfigOptions.retry_initial_delay],
                   max_delay=self.conf[ConfigOptions.retry_max_delay],
                   backoff=self.conf[ConfigOptions.retry_backoff],
                   jitter=(self.conf[ConfigOptions.retry_jitter_min],
                           self.conf[ConfigOptions.retry_jitter_max]))

    # Build http header
    def _build_header(self):

        headers = {
            HeaderKeys.content_type: self.conf[ConfigOptions.content_type],
            HeaderKeys.content_encoding: self.conf[ConfigOptions.content_encoding]
        }

        config_keys = self.conf.keys()

        # Add sumo specific header content
        sumo_config_keys = [ConfigOptions.source_name, ConfigOptions.host_name,
                            ConfigOptions.source_category]
        sumo_header_keys = [HeaderKeys.x_sumo_source, HeaderKeys.x_sumo_host,
                            HeaderKeys.x_sumo_category]
        for (config_key, header_key) in zip(sumo_config_keys, sumo_header_keys):
            if config_key in config_keys:
                headers[header_key] = self.conf[config_key]

        # Add custom dimension_tags specified in conf
        if ConfigOptions.dimension_tags in config_keys:
            headers[HeaderKeys.x_sumo_dimensions] = \
                MetricsConverter.tags_to_str(self._gen_config_dimension_tags())

        # Add custom meta_tags specified in conf
        if ConfigOptions.meta_tags in config_keys:
            headers[HeaderKeys.x_sumo_metadata] = \
                MetricsConverter.tags_to_str(self._gen_config_meta_tags())

        return headers

    # Generate dimension_tags from config
    def _gen_config_dimension_tags(self):

        return [MetricsConverter.gen_tag(k, v) for k, v in
                self.conf[ConfigOptions.dimension_tags].items()]

    # Generate meta_tags from config
    def _gen_config_meta_tags(self):

        return [MetricsConverter.gen_tag(k, v) for k, v in
                self.conf[ConfigOptions.meta_tags].items()]

    # Encode body with specified compress method gzip/deflate
    @staticmethod
    def _encode_body(body):
        return zlib.compress(str('\n'.join(body)))
