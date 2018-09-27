from unittest.mock import patch

from validation.headers import check_header_validity


def test_is_valid_header_when_is_dev_and_header_is_local_host():
    # Given
    header = 'localhost'


    # When
    with patch('validation.headers.IS_DEV', True):
        is_valid_header = check_header_validity(header)

    # Then
    assert is_valid_header


def test_is_not_valid_header_when_is_staging_and_header_is_local_host():
    # Given
    header = 'localhost'

    # When
    with patch('validation.headers.IS_STAGING', True), patch('validation.headers.IS_DEV', False):
        is_valid_header = check_header_validity(header)

    # Then
    assert not is_valid_header


def test_is_valid_header_when_is_staging_and_header_is_pro_passculture_staging():
    # Given
    header = 'pro.passculture-staging.beta.gouv.fr'

    # When
    with patch('validation.headers.IS_STAGING', True), patch('validation.headers.IS_DEV', False):
        is_valid_header = check_header_validity(header)

    # Then
    assert is_valid_header


def test_is_valid_header_when_is_staging_and_header_is_app_passculture_staging():
    # Given
    header = 'app.passculture-staging.beta.gouv.fr'

    # When
    with patch('validation.headers.IS_STAGING', True), patch('validation.headers.IS_DEV', False):
        is_valid_header = check_header_validity(header)

    # Then
    assert is_valid_header


def test_is_not_valid_header_when_not_staging_not_dev_and_header_is_app_passculture_staging():
    # Given
    header = 'app.passculture-staging.beta.gouv.fr'

    # When
    with patch('validation.headers.IS_STAGING', False), patch('validation.headers.IS_DEV', False):
        is_valid_header = check_header_validity(header)

    # Then
    assert not is_valid_header


def test_not_valid_header_when_not_staging_not_dev_and_header_is_app_passculture():
    # Given
    header = 'app.passculture.beta.gouv.fr'

    # When
    with patch('validation.headers.IS_STAGING', False), patch('validation.headers.IS_DEV', False):
        is_valid_header = check_header_validity(header)

    # Then
    assert is_valid_header


def test_not_valid_header_when_not_staging_not_dev_and_header_is_pro_passculture():
    # Given
    header = 'pro.passculture.beta.gouv.fr'

    # When
    with patch('validation.headers.IS_STAGING', False), patch('validation.headers.IS_DEV', False):
        is_valid_header = check_header_validity(header)

    # Then
    assert is_valid_header