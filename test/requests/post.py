# -*- coding: utf-8 -*-


class PostResponseDecider:
    def __init__(self):
        self.raise_recoverable_exception = False
        self.raise_unrecoverable_exception = False
        self.exception = None
        self.stop_raise_exception_after = 0
        self.current_retry_number = 0

    def reset(self):
        self.raise_recoverable_exception = False
        self.raise_unrecoverable_exception = False
        self.exception = None
        self.stop_raise_exception_after = 0
        self.current_retry_number = 0

    def set(
        self,
        raise_http_error=False,
        raise_exception=False,
        exception=None,
        stop_raise_exception_after=0,
        current_retry_number=0,
    ):
        self.raise_recoverable_exception = raise_http_error
        self.raise_unrecoverable_exception = raise_exception
        self.exception = exception
        self.stop_raise_exception_after = stop_raise_exception_after
        self.current_retry_number = current_retry_number


class MockServer:
    def __init__(self):
        self.url = None
        self.data = []
        self.headers = None

    def reset(self):
        self.url = None
        self.data = []
        self.headers = None


class MockResponse:
    def __init__(self):
        self.status_code = 200
        self.request = "test_request"

    def reset(self):
        self.status_code = 200

    def set(self, status_code):
        self.status_code = status_code


post_response_decider = PostResponseDecider()
mock_server = MockServer()
mock_response = MockResponse()


def post(url, data, headers):
    if post_response_decider.raise_recoverable_exception:
        if (
            post_response_decider.current_retry_number
            >= post_response_decider.stop_raise_exception_after
        ):
            return success(url, data, headers)
        else:
            raise_exception()
    elif post_response_decider.raise_unrecoverable_exception:
        raise_exception()
    else:
        return success(url, data, headers)


def raise_exception():
    exception = post_response_decider.exception
    exception.response = mock_response
    exception.message = "Http error with error code %s " % mock_response.status_code
    post_response_decider.current_retry_number += 1
    raise exception


def success(url, data, headers):
    mock_server.url = url
    mock_server.headers = headers
    mock_server.data.append(data)
    return mock_response
