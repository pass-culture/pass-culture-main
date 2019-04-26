from unittest.mock import patch

import re

from validation.headers import check_origin_header_validity


def test_is_valid_header_when_is_dev_and_header_is_local_host_for_normal_endpoint():
    # Given
    header_origin = 'http://localhost:3000'
    endpoint = 'list_offers'

    # When
    with patch('validation.headers.ENV', 'development'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert is_valid_header


def test_is_valid_header_when_is_testing_and_header_is_local_host_for_normal_endpoint():
    # Given
    header_origin = 'http://localhost:3000'
    endpoint = 'list_offers'

    # When
    with patch('validation.headers.ENV', 'testing'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert is_valid_header


def test_is_not_valid_header_when_is_staging_and_header_is_local_host_for_normal_endpoint():
    # Given
    header_origin = 'http://localhost:3000'
    endpoint = 'list_offers'

    # When
    with patch('validation.headers.ENV', 'staging'), patch('validation.headers.API_URL',
                                                           'https://backend.passculture-staging.beta.gouv.fr'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert not is_valid_header


def test_is_valid_header_when_header_not_in_whitelist_for_exception_endpoint():
    # Given
    header_origin = 'http://random.url.com'
    endpoint = 'patch_booking_by_token'

    # When
    with patch('validation.headers.ENV', 'staging'), patch('validation.headers.API_URL',
                                                           'https://backend.passculture-staging.beta.gouv.fr'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert is_valid_header


def test_is_valid_header_when_is_staging_and_header_is_pro_passculture_staging_for_normal_endpoint():
    # Given
    header_origin = 'http://pro.passculture-staging.beta.gouv.fr'
    endpoint = 'list_offers'

    # When
    with patch('validation.headers.ENV', 'staging'), patch('validation.headers.API_URL',
                                                           'https://backend.passculture-staging.beta.gouv.fr'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert is_valid_header


def test_is_valid_header_when_is_staging_and_header_is_app_passculture_staging_for_normal_endpoint():
    # Given
    header_origin = 'http://app.passculture-staging.beta.gouv.fr'
    endpoint = 'list_offers'

    # When
    with patch('validation.headers.ENV', 'staging'), patch('validation.headers.API_URL',
                                                           'https://backend.passculture-staging.beta.gouv.fr'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert is_valid_header


def test_is_not_valid_header_when_not_staging_not_dev_and_header_is_app_passculture_staging_for_normal_endpoint():
    # Given
    header_origin = 'http://app.passculture-staging.beta.gouv.fr'
    endpoint = 'list_offers'

    # When
    with patch('validation.headers.ENV', 'production'), patch('validation.headers.API_URL',
                                                              'https://backend.passculture.beta.gouv.fr'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert not is_valid_header


def test_is_valid_header_when_not_staging_not_dev_for_exception_endpoint_and_exception_endpoint():
    # Given
    header_origin = 'http://random.url.fr'
    endpoint = 'patch_booking_by_token'

    # When
    with patch('validation.headers.ENV', 'production'), patch('validation.headers.API_URL',
                                                              'https://backend.passculture.beta.gouv.fr'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert is_valid_header


def test_is_valid_header_when_not_staging_not_dev_and_header_is_app_passculture_for_normal_endpoint():
    # Given
    header_origin = 'http://app.passculture.beta.gouv.fr'
    endpoint = 'list_offers'

    # When
    with patch('validation.headers.ENV', 'production'), patch('validation.headers.API_URL',
                                                              'https://backend.passculture.beta.gouv.fr'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert is_valid_header


def test_not_valid_header_when_not_staging_not_dev_and_header_is_pro_passculture_for_normal_endpoint():
    # Given
    header_origin = 'http://pro.passculture.beta.gouv.fr'
    endpoint = 'list_offers'

    # When
    with patch('validation.headers.ENV', 'production'), patch('validation.headers.API_URL',
                                                              'https://backend.passculture.beta.gouv.fr'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert is_valid_header


def test_is_valid_header_when_not_staging_not_dev_and_header_is_pro_passculture_for_exception_endpoint():
    # Given
    header_origin = 'http://random.url.frv'
    endpoint = 'patch_booking_by_token'

    # When
    with patch('validation.headers.ENV', 'production'), patch('validation.headers.API_URL',
                                                              'https://backend.passculture.beta.gouv.fr'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert is_valid_header


def test_any_origin_header_is_valid_on_endpoint_validate_venue():
    # Given
    header_origin = 'http://random.url.fr'
    endpoint = 'validate_venue'

    # When
    with patch('validation.headers.ENV', 'production'), patch('validation.headers.API_URL',
                                                              'https://backend.passculture.beta.gouv.fr'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert is_valid_header


def test_is_valid_header_when_url_is_authorized_in_subdomain():
    # Given
    header_origin = 'https://poc.passculture.app'
    endpoint = 'list_offers'

    # When
    with patch('validation.headers.ENV', 'testing'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert is_valid_header


def test_is_invalid_header_when_url_is_not_known():
    # Given
    header_origin = 'https://poc.fr'
    endpoint = 'list_offers'

    # When
    with patch('validation.headers.ENV', 'testing'):
        is_valid_header = check_origin_header_validity(header_origin, endpoint, '/')

    # Then
    assert not is_valid_header
