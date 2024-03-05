import logging

import pytest

from pcapi.utils import requests


def test_wrapper_logs_info_on_success(requests_mock, caplog):
    requests_mock.get("https://example.com", text="response")

    with caplog.at_level(logging.INFO):
        response = requests.get("https://example.com")
        assert response.text == "response"

    log = caplog.records[0]
    assert log.message == "External service called"
    assert log.url == "https://example.com/"
    assert log.statusCode == 200
    assert log.duration is not None


def test_wrapper_logs_warning_on_failure(requests_mock, caplog):
    exception = requests.exceptions.ConnectTimeout
    requests_mock.get("https://example.com", exc=exception)

    with pytest.raises(exception):
        with caplog.at_level(logging.WARNING):
            requests.get("https://example.com")

    log = caplog.records[0]
    assert log.message == "Call to external service failed with "
    assert log.url == "https://example.com"
    assert log.method == "GET"


def test_wrapper_redacts_url(requests_mock, caplog):
    requests_mock.get("https://example.com/success")
    exception = requests.exceptions.ConnectTimeout
    requests_mock.get("https://example.com/failure", exc=exception)

    with caplog.at_level(logging.INFO):
        requests.get("https://example.com/success?token=secret")
    log = caplog.records[0]
    assert log.url == "https://example.com/success?token=[REDACTED]"

    with pytest.raises(exception):
        with caplog.at_level(logging.WARNING):
            requests.get("https://example.com/failure?token=secret")
    log = caplog.records[-1]
    assert log.url == "https://example.com/failure?token=[REDACTED]"


def test_wrapper_sets_default_timeout(requests_mock):
    requests_mock.get("https://example.com")

    requests.get("https://example.com")

    assert requests_mock.last_request.timeout == 10


def test_wrapper_keeps_timeout_if_given(requests_mock):
    requests_mock.get("https://example.com")

    requests.get("https://example.com", timeout=2)

    assert requests_mock.last_request.timeout == 2


@pytest.mark.parametrize("verb", ["get", "post", "put", "delete"])
def test_wrapper_is_used_when_calling_verbs(requests_mock, caplog, verb):
    getattr(requests_mock, verb)("https://example.com", text="response")

    with caplog.at_level(logging.INFO):
        response = getattr(requests, verb)("https://example.com")
        assert response.text == "response"

    log = caplog.records[0]
    assert log.message == "External service called"


@pytest.mark.parametrize("verb", ["get", "post", "put", "delete"])
def test_wrapper_is_used_when_using_session(requests_mock, caplog, verb):
    getattr(requests_mock, verb)("https://example.com", text="response")

    session = requests.Session()
    with caplog.at_level(logging.INFO):
        response = getattr(session, verb)("https://example.com")
        assert response.text == "response"

    log = caplog.records[0]
    assert log.message == "External service called"
