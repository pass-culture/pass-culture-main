from unittest.mock import Mock

import pytest

from models import ApiErrors, ApiKey, User, PcObject
from tests.conftest import clean_database
from tests.test_utils import create_offerer, create_user, create_user_offerer
from validation.users import check_valid_signup_webapp,\
    check_user_can_validate_bookings,\
    check_user_can_validate_v2_bookings,\
    check_valid_signup_pro,\
    check_user_with_api_key_can_validate_bookings
from utils.token import random_token

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

class CheckUserCanValidateBookingsTest:
    class UserHasRightsTest:
        @clean_database
        def test_check_user_can_validate_bookings_return_true_when_user_is_authenticated_and_has_editor_rights_on_booking(
                self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer, None)
            PcObject.save(user, offerer, user_offerer)

            # When
            result = check_user_can_validate_bookings(user, offerer.id)

            # Then
            assert result is True

        @clean_database
        def test_check_user_can_validate_bookings_return_true_when_user_has_api_key_and_has_editor_rights_on_booking(
                self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer, None)

            PcObject.save(user, offerer, user_offerer)

            validApiKey = ApiKey()
            validApiKey.value = random_token(64)
            validApiKey.offererId = offerer.id

            PcObject.save(validApiKey)

            result = check_user_with_api_key_can_validate_bookings(validApiKey, offerer.id)

            # Then
            assert result is True

        @clean_database
        def test_check_user_can_validate_v2_bookings_return_true_when_user_has_editor_rights_on_booking(
                self, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer, None)

            PcObject.save(user, offerer, user_offerer)

            result = check_user_can_validate_v2_bookings(user, offerer.id)

            # Then
            assert result is True

    class UserHaveNoRights:
        def test_check_user_can_validate_bookings_return_false_when_user_is_not_authenticated(self, app):
            # Given
            user = User()
            user.is_authenticated = False

            # When
            result = check_user_can_validate_bookings(user, None)

            # Then
            assert result is False


        def test_check_user_can_validate_bookings_raise_api_error_when_user_is_authenticated_and_does_not_have_editor_rights_on_booking(
                self, app):
            # Given
            user = User()
            user.is_authenticated = True

            # When
            with pytest.raises(ApiErrors) as errors:
                check_user_can_validate_bookings(user, None)

            # Then
            assert errors.value.errors['global'] == ["Cette contremarque n'a pas été trouvée"]

        def test_check_user_can_validate_v2_bookings_raise_api_error_when_user_is_authenticated_and_does_not_have_editor_rights_on_booking(
                self, app):
            # Given
            user = User()
            user.is_authenticated = True

            # When
            with pytest.raises(ApiErrors) as errors:
                check_user_can_validate_v2_bookings(user, None)

            # Then
            assert errors.value.errors['user'] == ["Vous n'avez pas les droits suffisants pour éditer cette contremarque."]

        def test_check_user_with_api_key_can_validate_bookings_raise_api_error_when_user_is_authenticated_and_does_not_have_editor_rights_on_booking(
                self, app):
            # Given
            validApiKey = ApiKey()
            validApiKey.value = random_token(64)
            validApiKey.offererId = 67

            # When
            with pytest.raises(ApiErrors) as errors:
                check_user_with_api_key_can_validate_bookings(validApiKey, None)

            # Then
            assert errors.value.errors['user'] == ["Vous n'avez pas les droits suffisants pour éditer cette contremarque."]
