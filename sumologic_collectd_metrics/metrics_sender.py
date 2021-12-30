# -*- coding: utf-8 -*-

try:
    from StringIO import StringIO as CompatibleIO
except ImportError:
    from io import BytesIO as CompatibleIO

import gzip
import zlib

import requests
from retry.api import retry_call

from .metrics_config import ConfigOptions
from .metrics_converter import gen_tag, tags_to_str
from .metrics_util import RecoverableException
from .timer import Timer


class HeaderKeys(object):
    """
    Http header keys
    """

    content_type = "Content-Type"
    content_encoding = "Content-Encoding"
    x_sumo_source = "X-Sumo-Name"
    x_sumo_host = "X-Sumo-Host"
    x_sumo_category = "X-Sumo-Category"
    x_sumo_dimensions = "X-Sumo-Dimensions"
    x_sumo_metadata = "X-Sumo-Metadata"
    x_sumo_client = "X-Sumo-Client"


class MetricsSender(Timer):
    """
    Fetches metrics batch from MetricsBuffer and post the http request with error handling and retry
    """

    def __init__(self, conf, met_buf, collectd):
        """
        Init MetricsSender with conf and met_buf
        """

        self.collectd = collectd
        self.sent_batch_count = 0
        self.sent_metric_count = 0
        Timer.__init__(
            self, conf[ConfigOptions.http_post_interval], self._request_scheduler
        )
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
        except Exception as e:
            self.collectd.warning(
                "Sending metrics batch %s failed after all retries due to %s. "
                "Put metrics batch into failed metrics buffer." % (batch, str(e))
            )
            self.buffer.put_failed_batch(batch)

    # Send metrics batch via https with error handling
    # Exceptions defined in https://github.com/requests/requests/blob/master/requests/exceptions.py
    def _send_request(self, headers, body):

        try:
            self.collectd.debug(
                "Sending https request with headers %s, body %s" % (headers, body)
            )

            response = requests.post(
                self.conf[ConfigOptions.url],
                data=self.encode_body(body),
                headers=headers,
            )

            self.collectd.info(
                "Sent https request with batch_size=%d got response_code=%s"
                % (len(body), response.status_code)
            )
            self.sent_batch_count += 1
            self.sent_metric_count += len(body)
        except requests.exceptions.HTTPError as e:
            self.fail_with_recoverable_exception("An HTTP error occurred", body, e)
        except requests.exceptions.ConnectionError as e:
            self.fail_with_recoverable_exception("A Connection error occurred", body, e)
        except requests.exceptions.Timeout as e:
            self.fail_with_recoverable_exception("The request timed out", body, e)
        except requests.exceptions.TooManyRedirects as e:
            self.fail_with_recoverable_exception("Too many redirects", body, e)
        except requests.exceptions.StreamConsumedError as e:
            self.fail_with_recoverable_exception(
                "The content for this response was already consumed", body, e
            )
        except requests.exceptions.RetryError as e:
            self.fail_with_recoverable_exception("Custom retries logic failed", body, e)
        except requests.exceptions.ChunkedEncodingError as e:
            self.fail_with_recoverable_exception(
                "The server declared chunked encoding but sent an invalid chunk",
                body,
                e,
            )
        except requests.exceptions.ContentDecodingError as e:
            self.fail_with_recoverable_exception("Failed to decode response", body, e)
        except requests.exceptions.URLRequired as e:
            self.fail_with_recoverable_exception(
                "A valid URL is required to make a request", body, e
            )
        except requests.exceptions.MissingSchema as e:
            self.fail_with_recoverable_exception(
                "The URL schema (e.g. http or https) is missing", body, e
            )
        except requests.exceptions.InvalidSchema as e:
            self.fail_with_recoverable_exception("See schemas in defaults.py", body, e)
        except requests.exceptions.InvalidURL as e:
            self.fail_with_recoverable_exception(
                "The URL provided was invalid", body, e
            )
        except Exception as e:
            self.fail_with_recoverable_exception("unknown exception", body, e)

    # Send http request with retries
    def _send_request_with_retries(self, batch):

        retry_call(
            self._send_request,
            fargs=[self.http_headers, batch],
            exceptions=RecoverableException,
            tries=self.conf[ConfigOptions.retry_max_attempts],
            delay=self.conf[ConfigOptions.retry_initial_delay],
            max_delay=self.conf[ConfigOptions.retry_max_delay],
            backoff=self.conf[ConfigOptions.retry_backoff],
            jitter=(
                self.conf[ConfigOptions.retry_jitter_min],
                self.conf[ConfigOptions.retry_jitter_max],
            ),
        )

    # Build http header
    def _build_header(self):

        headers = {
            HeaderKeys.content_type: self.conf[ConfigOptions.content_type],
            HeaderKeys.content_encoding: self.conf[ConfigOptions.content_encoding],
            HeaderKeys.x_sumo_client: "collectd-plugin",
        }

        config_keys = self.conf.keys()

        # Add sumo specific header content
        sumo_config_keys = [
            ConfigOptions.source_name,
            ConfigOptions.host_name,
            ConfigOptions.source_category,
        ]
        sumo_header_keys = [
            HeaderKeys.x_sumo_source,
            HeaderKeys.x_sumo_host,
            HeaderKeys.x_sumo_category,
        ]
        for (config_key, header_key) in zip(sumo_config_keys, sumo_header_keys):
            if config_key in config_keys:
                headers[header_key] = self.conf[config_key]

        # Add custom dimension_tags specified in conf
        if ConfigOptions.dimension_tags in config_keys:
            headers[HeaderKeys.x_sumo_dimensions] = tags_to_str(
                self._gen_config_dimension_tags(), sep=","
            )

        # Add custom meta_tags specified in conf
        if ConfigOptions.meta_tags in config_keys:
            headers[HeaderKeys.x_sumo_metadata] = tags_to_str(
                self._gen_config_meta_tags(), sep=","
            )

        return headers

    # Generate dimension_tags from config
    def _gen_config_dimension_tags(self):

        return [gen_tag(k, v) for k, v in self.conf[ConfigOptions.dimension_tags]]

    # Generate meta_tags from config
    def _gen_config_meta_tags(self):

        return [gen_tag(k, v) for k, v in self.conf[ConfigOptions.meta_tags]]

    # Encode body with specified compress method gzip/deflate
    def encode_body(self, body):
        body_str = "\n".join(body).encode("utf-8")
        content_encoding = self.conf[ConfigOptions.content_encoding]
        if content_encoding == "deflate":
            return zlib.compress(body_str)

        if content_encoding == "gzip":
            encoded_stream = CompatibleIO()
            with GzipFile(fileobj=encoded_stream, mode="w") as file:
                file.write(body_str)
            return encoded_stream.getvalue()

        return body_str

    def fail_with_recoverable_exception(self, msg, batch, e):
        """
        Warn about exception and raise RecoverableException
        """

        self.collectd.warning(
            msg + ": Sending batch with size %s failed with recoverable "
            "exception %s. Retrying" % (len(batch), str(e))
        )
        raise RecoverableException(e)


# Fix GzipFile incompatibility with python 2.6
# https://mail.python.org/pipermail/tutor/2009-November/072957.html
class GzipFile(gzip.GzipFile):
    def __enter__(self, *args):
        if hasattr(gzip.GzipFile, "__enter__"):
            return gzip.GzipFile.__enter__(self)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(gzip.GzipFile, "__exit__"):
            return gzip.GzipFile.__exit__(self, exc_type, exc_value, traceback)

        return self.close()
