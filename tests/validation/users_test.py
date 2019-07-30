from unittest.mock import Mock

import pytest

from models import ApiErrors, User, PcObject
from tests.conftest import clean_database
from tests.test_utils import create_offerer, create_user, create_user_offerer
from validation.users import check_valid_signup, check_user_can_validate_bookings


def test_check_valid_signup_raises_api_error_if_not_contact_ok():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'email': 'test@email.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup(mocked_request)

    # Then
    assert errors.value.errors['contact_ok'] == ['Vous devez obligatoirement cocher cette case.']


def test_check_valid_signup_raises_api_error_if_contact_ok_false():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'contact_ok': False, 'email': 'test@email.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup(mocked_request)

    # Then
    assert errors.value.errors['contact_ok'] == ['Vous devez obligatoirement cocher cette case.']


def test_check_valid_signup_raises_api_error_if_contact_ok_random_string():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'contact_ok': 'ekoe', 'email': 'test@email.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup(mocked_request)

    # Then
    assert errors.value.errors['contact_ok'] == ['Vous devez obligatoirement cocher cette case.']


def test_check_valid_signup_raises_api_error_if_no_password():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'contact_ok': True, 'email': 'test@email.com'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup(mocked_request)

    # Then
    assert errors.value.errors['password'] == ['Vous devez renseigner un mot de passe.']


def test_check_valid_signup_raises_api_error_if_no_email():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'contact_ok': True, 'password': 'ozkfoepzfze'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup(mocked_request)

    # Then
    assert errors.value.errors['email'] == ['Vous devez renseigner un email.']


def test_check_valid_signup_raises_api_error_if_no_phone():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'contact_ok': True, 'email': 'john.doe@test.fr', 'password': 'ozkfoepzfze'}

    # When
    with pytest.raises(ApiErrors) as errors:
        check_valid_signup(mocked_request)

    # Then
    assert errors.value.errors['phoneNumber'] == ['Vous devez renseigner un numéro de téléphone.']


def test_check_valid_signup_does_not_raise_api_error_if_contact_ok_is_true_has_password_and_email_and_phone_number():
    # Given
    mocked_request = Mock()
    mocked_request.json = {'password': '87YHJKS*nqde', 'email': 'test@email.com', 'contact_ok': True, 'phoneNumber': '0102030405'}

    # When
    try:
        check_valid_signup(mocked_request)
    except ApiErrors:
        # Then
        assert False


def test_check_user_can_validate_bookings_return_false_when_user_is_not_authenticated(app):
    # Given
    user = User()
    user.is_authenticated = False

    # When
    result = check_user_can_validate_bookings(user, None)

    # Then
    assert result is False


@clean_database
def test_check_user_can_validate_bookings_return_true_when_user_is_authenticated_and_has_editor_rights_on_booking(app):
    # Given
    user = create_user()
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer, None)
    PcObject.save(user, offerer, user_offerer)

    # When
    result = check_user_can_validate_bookings(user, offerer.id)

    # Then
    assert result is True


def test_check_user_can_validate_bookings_raise_api_error_when_user_is_authenticated_and_does_not_have_editor_rights_on_booking(
        app):
    # Given
    user = User()
    user.is_authenticated = True

    # When
    with pytest.raises(ApiErrors) as errors:
        check_user_can_validate_bookings(user, None)

    # Then
    assert errors.value.errors['global'] == ["Cette contremarque n'a pas été trouvée"]
