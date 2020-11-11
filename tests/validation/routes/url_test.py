import pytest

from pcapi.models import ApiErrors
from pcapi.validation.routes.url import is_url_safe


def test_is_url_safe_does_not_raise_an_error_if_url_is_none():
    # given
    url = None

    # when
    try:
        is_url_safe(url)
    except ApiErrors:
        # then
        assert False


def test_is_url_safe_does_not_raise_an_error_if_url_is_empty():
    # given
    url = ""

    # when
    try:
        is_url_safe(url)
    except ApiErrors:
        # then
        assert False


def test_is_url_safe_does_not_raise_an_error_if_url_starts_with_http():
    # given
    url = "http://some.valid.url"

    # when
    try:
        is_url_safe(url)
    except ApiErrors:
        # then
        assert False


def test_is_url_safe_does_not_raise_an_error_if_url_starts_with_https():
    # given
    url = "https://some.valid.url"

    # when
    try:
        is_url_safe(url)
    except ApiErrors:
        # then
        assert False


def test_is_url_safe_raises_an_error_if_url_does_not_start_with_http():
    # given
    url = "htpp://some.invalid.url"

    # when
    with pytest.raises(ApiErrors) as e:
        is_url_safe(url)

    # then
    assert e.value.errors["url"] == ['L\'URL doit commencer par "http://" ou "https://"']


def test_is_url_safe_raises_an_error_if_url_does_not_start_with_https():
    # given
    url = "httpssss://some.invalid.url"

    # when
    with pytest.raises(ApiErrors) as e:
        is_url_safe(url)

    # then
    assert e.value.errors["url"] == ['L\'URL doit commencer par "http://" ou "https://"']


def test_is_url_safe_raises_an_error_if_url_starts_with_javascript():
    # given
    url = "javascript:alert('XSS')"

    # when
    with pytest.raises(ApiErrors) as e:
        is_url_safe(url)

    # then
    assert e.value.errors["url"] == ['L\'URL doit commencer par "http://" ou "https://"']


def test_is_url_safe_raises_an_error_if_url_starts_with_encoded_javascript():
    # given
    url = "j&#X41vascript:alert('XSS')"

    # when
    with pytest.raises(ApiErrors) as e:
        is_url_safe(url)

    # then
    assert e.value.errors["url"] == ['L\'URL doit commencer par "http://" ou "https://"']
