from unittest.mock import patch

import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as user_models
from pcapi.models.api_errors import ApiErrors
from pcapi.validation.models.user import validate


@pytest.mark.usefixtures("db_session")
class UserAlreadyExistsTest:
    def test_new_user_with_existing_email(self):
        existing = users_factories.UserFactory()
        user = users_factories.UserFactory.build(id=None, email=existing.email)

        api_errors = ApiErrors()
        api_error = validate(user, api_errors)

        assert api_error.errors["email"] == ["Un compte lié à cet email existe déjà"]

    def test_new_user_with_different_email(self):
        users_factories.UserFactory(email="existing@example.com")
        user = users_factories.UserFactory.build(id=None, email="new@example.com")

        api_errors = ApiErrors()
        api_error = validate(user, api_errors)

        assert not api_error.errors

    def test_existing_user(self):
        user = users_factories.UserFactory()

        api_errors = ApiErrors()
        api_error = validate(user, api_errors)

        assert not api_error.errors


class EmailTest:
    def test_should_return_error_message_when_email_does_not_contain_at_sign(self, app):
        # Given
        user = users_factories.UserFactory.build(email="joel.example.com")
        api_errors = ApiErrors()

        # When
        api_error = validate(user, api_errors)

        # Then
        assert api_error.errors["email"] == ["L’email doit contenir un @."]

    @patch("pcapi.core.users.repository.find_user_by_email")
    def test_should_not_return_error_message_when_user_email_is_correct(self, mocked_find_user_by_email):
        # Given
        user = users_factories.UserFactory.build(email="joel@example.com")
        mocked_find_user_by_email.return_value = None
        api_errors = ApiErrors()

        # When
        api_error = validate(user, api_errors)

        # Then
        assert not api_error.errors


class AdminTest:
    def test_should_return_error_message_when_admin_user_is_beneficiary(self, app):
        # Given
        user = users_factories.UserFactory.build(
            roles=[user_models.UserRole.BENEFICIARY, user_models.UserRole.ADMIN],
        )
        api_errors = ApiErrors()

        # When
        api_error = validate(user, api_errors)

        # Then
        assert api_error.errors["is_beneficiary"] == ["Admin ne peut pas être bénéficiaire"]


class PasswordTest:
    def test_should_return_error_message_when_user_password_is_less_than_8_characters(self, app):
        # Given
        user = users_factories.UserFactory.build()
        user.setPassword("Jo")
        api_errors = ApiErrors()

        # When
        api_error = validate(user, api_errors)

        # Then
        assert api_error.errors["password"] == ["Tu dois saisir au moins 8 caractères."]

    @patch("pcapi.core.users.repository.find_user_by_email")
    def test_should_not_return_error_message_when_user_password_is_correct(self, mocked_find_user_by_email):
        # Given
        user = users_factories.UserFactory.build()
        user.setPassword("JoelDupont")
        mocked_find_user_by_email.return_value = None
        api_errors = ApiErrors()

        # When
        api_error = validate(user, api_errors)

        # Then
        assert not api_error.errors
