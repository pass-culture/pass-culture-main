from unittest.mock import Mock

import pytest

from models import ApiErrors
from validation.users import check_valid_signup


@pytest.mark.standalone
def test_check_valid_signup_raises_api_error_if_not_contact_ok():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'email': 'test@email.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup(mocked_request)

    # Then
    assert errors.value.errors['contact_ok'] == ['Vous devez obligatoirement cocher cette case.']


@pytest.mark.standalone
def test_check_valid_signup_raises_api_error_if_contact_ok_false():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'contact_ok': False, 'email': 'test@email.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup(mocked_request)

    # Then
    assert errors.value.errors['contact_ok'] == ['Vous devez obligatoirement cocher cette case.']


@pytest.mark.standalone
def test_check_valid_signup_raises_api_error_if_contact_ok_random_string():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde','contact_ok': 'ekoe', 'email': 'test@email.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup(mocked_request)

    # Then
    assert errors.value.errors['contact_ok'] == ['Vous devez obligatoirement cocher cette case.']


@pytest.mark.standalone
def test_check_valid_signup_raises_api_error_if_no_password():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'contact_ok': True, 'email': 'test@email.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup(mocked_request)

    # Then
    assert errors.value.errors['password'] == ['Vous devez renseigner un mot de passe.']


@pytest.mark.standalone
def test_check_valid_signup_raises_api_error_if_no_email():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'contact_ok': True, 'password': 'ozkfoepzfze'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup(mocked_request)

    # Then
    assert errors.value.errors['email'] == ['Vous devez renseigner un email.']


@pytest.mark.standalone
def test_check_valid_signup_does_not_raise_api_error_if_contact_ok_is_true_has_password_and_email():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'email': 'test@email.com', 'contact_ok': True}

    # When
    try:
        check_valid_signup(mocked_request)
    except ApiErrors:
        # Then
        assert False


@pytest.mark.standalone
def test_check_valid_signup_does_not_raise_api_error_if_contact_ok_is_true_has_password_and_email():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': 'lkefefjez', 'email': 'test@email.com', 'contact_ok': 'true'}

    # When
    try:
        check_valid_signup(mocked_request)
    except ApiErrors:
        # Then
        assert False
