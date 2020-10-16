from unittest import mock
from unittest.mock import Mock, \
    patch

import pytest
from requests import Response

from pcapi.utils.requests import _wrapper, \
    _log_call_to_external_service


class RequestWrapperTest:
    def test_call_given_request_function_with_params(self):
        # given
        mocked_request_function = Mock()

        # when
        _wrapper(mocked_request_function, 'GET', 'https://example.net')

        # then
        mocked_request_function.assert_called_once_with(method='GET', url='https://example.net',timeout=10, hooks={'response': mock.ANY})

    def test_should_propagate_any_exception(self):
        # given
        mocked_request_function = Mock(side_effect=Exception())

        # when
        with pytest.raises(Exception):
            _wrapper(mocked_request_function, 'GET', 'https://example.net')

class RequestHookTest:
    @patch('pcapi.utils.requests.json_logger.info')
    def test_should_log_the_response_result(self, json_logger_info):
        # given
        fake_response = Response()
        fake_response.status_code = 200

        # when
        _log_call_to_external_service(fake_response)

        # then
        json_logger_info.assert_called_once()
