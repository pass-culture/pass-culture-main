from unittest.mock import Mock

import pytest

from models import ApiErrors
from validation.users import check_valid_signup_webapp,\
    check_valid_signup_pro


def test_check_valid_signup_webapp_raises_api_error_if_not_contact_ok():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'email': 'test@email.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup_webapp(mocked_request)

    # Then
    assert errors.value.errors['contact_ok'] == ['Vous devez obligatoirement cocher cette case.']


def test_check_valid_signup_webapp_raises_api_error_if_contact_ok_false():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'contact_ok': False, 'email': 'test@email.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup_webapp(mocked_request)

    # Then
    assert errors.value.errors['contact_ok'] == ['Vous devez obligatoirement cocher cette case.']


def test_check_valid_signup_webapp_raises_api_error_if_contact_ok_random_string():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'contact_ok': 'ekoe', 'email': 'test@email.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup_webapp(mocked_request)

    # Then
    assert errors.value.errors['contact_ok'] == ['Vous devez obligatoirement cocher cette case.']


def test_check_valid_signup_webapp_raises_api_error_if_no_password():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'contact_ok': True, 'email': 'test@email.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup_webapp(mocked_request)

    # Then
    assert errors.value.errors['password'] == ['Vous devez renseigner un mot de passe.']


def test_check_valid_signup_webapp_raises_api_error_if_password_is_not_strong_enough():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'contact_ok': True, 'email': 'test@email.com', 'password': 'ABC'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup_webapp(mocked_request)

    # Then
    assert errors.value.errors['password'] == ['Le mot de passe doit faire au moins 12 caractères et contenir à minima 1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial parmi ''_-&?~#|^@=+.$,<>%*!:;']


def test_check_valid_signup_webapp_raises_api_error_if_no_email():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'contact_ok': True, 'password': 'ozkfoepzfze'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup_webapp(mocked_request)

    # Then
    assert errors.value.errors['email'] == ['Vous devez renseigner un email.']


def test_check_valid_signup_pro_raises_api_error_if_no_phone():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'contact_ok': True, 'email': 'john.doe@test.fr', 'password': 'ozkfoepzfze'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup_pro(mocked_request)

    # Then
    assert errors.value.errors['phoneNumber'] == ['Vous devez renseigner un numéro de téléphone.']


def test_check_valid_signup_webapp_does_not_raise_api_error_if_contact_ok_is_true_has_password_and_email():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'email': 'test@email.com', 'contact_ok': True}

    # When
    try:
        check_valid_signup_webapp(mocked_request)
    except ApiErrors:
        # Then
        assert False


def test_check_valid_signup_pro_does_not_raise_api_error_if_contact_ok_is_true_has_password_and_email_and_phone_number():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'email': 'test@email.com', 'contact_ok': True, 'phoneNumber': '0102030405'}

    # When
    try:
        check_valid_signup_webapp(mocked_request)
    except ApiErrors:
        # Then
        assert False
