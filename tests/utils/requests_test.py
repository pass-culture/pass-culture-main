from unittest import mock
from unittest.mock import Mock

import pytest
from requests import RequestException

from pcapi.utils.requests import _wrapper


class RequestWrapperTest:
    def test_call_given_request_function_with_params(self):
        # given
        mocked_request_function = Mock()

        # when
        _wrapper(mocked_request_function, 'GET', 'https://example.net')

        # then
        mocked_request_function.assert_called_once_with(method='GET', url='https://example.net',timeout=10)

    def test_should_propagate_any_exception(self):
        # given
        mocked_request_function = Mock(side_effect=RequestException())

        # when
        with pytest.raises(RequestException):
            _wrapper(mocked_request_function, 'GET', 'https://example.net')
