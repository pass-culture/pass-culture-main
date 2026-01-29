import logging
from urllib.parse import unquote

import pytest
import requests.models as real_requests_models  # noqa: TID251

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
    assert log.url == "https://example.com/"
    assert log.method == "GET"


@pytest.mark.parametrize(
    "parameter",
    [
        # API Particulier
        "recipient",
        "nomNaissance",
        "prenoms[]",
        "nomUsage",
        "anneeDateNaissance",
        "moisDateNaissance",
        "jourDateNaissance",
        "sexeEtatCivil",
        "codeCogInseePaysNaissance",
        "codeCogInseeCommuneNaissance",
        "annee",
        "mois",
        # Allociné and CDS
        "api_token",
        "token",
    ],
)
def test_wrapper_redacts_url(requests_mock, caplog, parameter):
    requests_mock.get("https://example.com/success")
    exception = requests.exceptions.ConnectTimeout
    requests_mock.get("https://example.com/failure", exc=exception)

    with caplog.at_level(logging.INFO):
        requests.get(f"https://example.com/success?{parameter}=secret")
    log = caplog.records[0]
    assert unquote(log.url) == f"https://example.com/success?{parameter}=[REDACTED]"

    with pytest.raises(exception):
        with caplog.at_level(logging.WARNING):
            requests.get(f"https://example.com/failure?{parameter}=secret")
    log = caplog.records[-1]
    assert unquote(log.url) == f"https://example.com/failure?{parameter}=[REDACTED]"


def test_redact_multiple_parameters_in_url(requests_mock, caplog):
    requests_mock.get("https://example.com/success")
    exception = requests.exceptions.ConnectTimeout
    requests_mock.get("https://example.com/failure", exc=exception)

    with caplog.at_level(logging.INFO):
        requests.get(
            "https://example.com/success?recipient=secret1&nomNaissance=secret2&prenoms[]=secret3&nomUsage=secret4"
        )
    log = caplog.records[0]
    assert (
        unquote(log.url)
        == "https://example.com/success?recipient=[REDACTED]&nomNaissance=[REDACTED]&prenoms[]=[REDACTED]&nomUsage=[REDACTED]"
    )

    with pytest.raises(exception):
        with caplog.at_level(logging.WARNING):
            requests.get(
                "https://example.com/failure?recipient=secret1&nomNaissance=secret2&prenoms[]=secret3&nomUsage=secret4"
            )
    log = caplog.records[-1]
    assert (
        unquote(log.url)
        == "https://example.com/failure?recipient=[REDACTED]&nomNaissance=[REDACTED]&prenoms[]=[REDACTED]&nomUsage=[REDACTED]"
    )


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
def test_wrapper_is_used_when_using_session_verbs(requests_mock, caplog, verb):
    getattr(requests_mock, verb)("https://example.com", text="response")

    session = requests.Session()
    with caplog.at_level(logging.INFO):
        response = getattr(session, verb)("https://example.com")
        assert response.text == "response"

    log = caplog.records[0]
    assert log.message == "External service called"


def test_wrapper_is_used_when_using_session_send(requests_mock, caplog):
    requests_mock.get("https://example.com", text="response")

    session = requests.Session()
    request = real_requests_models.Request(method="GET", url="https://example.com")
    request = session.prepare_request(request)

    with caplog.at_level(logging.INFO):
        response = session.send(request)
        assert response.text == "response"

    log = caplog.records[0]
    assert log.message == "External service called"
