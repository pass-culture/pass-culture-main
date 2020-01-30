import pytest

from models import ApiErrors, User
from validation.routes.users_authentifications import check_user_is_logged_in_or_email_is_provided


class CheckUserIsLoggedInOrEmailIsProvidedTest:
    def test_raises_an_error_when_no_email_nor_user_logged(self):
        # Given
        user = User()
        user.is_authenticated = False
        email = None

        # When
        with pytest.raises(ApiErrors) as excinfo:
            check_user_is_logged_in_or_email_is_provided(user, email)

        # Then
        assert excinfo.value.errors['email'] == [
            "Vous devez préciser l'email de l'utilisateur quand vous n'êtes pas connecté(e)"]

    def test_does_not_raise_error_when_email_is_provided(self):
        # Given
        user = User()
        user.is_authenticated = False
        email = 'fake@example.com'

        # When
        try:
            check_user_is_logged_in_or_email_is_provided(user, email)

        # Then
        except ApiErrors:
            assert False

    def test_does_not_raise_error_when_user_is_authenticated(self):
        # Given
        user = User()
        user.is_authenticated = True
        email = 'fake@example.com'

        # When
        try:
            check_user_is_logged_in_or_email_is_provided(user, email)

        # Then
        except ApiErrors:
            assert False
