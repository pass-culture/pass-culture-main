from urllib.parse import urlparse

from flask import url_for


def assert_url_equals(actual: str, expected: str) -> None:
    """
    Check that URL are the same, considering that query parameters may be in a different order
    """
    parsed_actual = urlparse(actual)
    parsed_expected = urlparse(expected)

    assert parsed_actual.scheme == parsed_expected.scheme
    assert parsed_actual.hostname == parsed_expected.hostname
    assert parsed_actual.port == parsed_expected.port
    assert parsed_actual.path == parsed_expected.path
    assert set(parsed_actual.query.split("&")) == set(parsed_expected.query.split("&"))


def assert_response_location(response, endpoint: str, **kwargs) -> None:
    assert response.location
    assert_url_equals(response.location, url_for(endpoint, **kwargs))
