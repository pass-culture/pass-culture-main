import pytest

from models import ApiErrors, User
from tests.conftest import clean_database
from validation.users_authentifications import check_user_is_logged_in_or_email_is_provided


class CheckUserIsLoggedInOrEmailIsProvidedTest:
    @clean_database
    def test_raises_an_error_when_no_email_nor_user_logged(self, app):
        # given
        user = User()
        user.is_authenticated = False
        email = None

        # when
        with pytest.raises(ApiErrors) as e:
            check_user_is_logged_in_or_email_is_provided(user, email)

        # then
        assert e.value.errors['email'] == [
            "Vous devez préciser l'email de l'utilisateur quand vous n'êtes pas connecté(e)"]

    def test_does_not_raise_error_when_email_is_provided(self, app):
        # given
        user = User()
        user.is_authenticated = False
        email = 'fake@email.com'

        # When
        try:
            check_user_is_logged_in_or_email_is_provided(user, email)

        # Then
        except:
            assert False

    def test_does_not_raise_error_when_user_is_authenticated(self, app):
        # given
        user = User()
        user.is_authenticated = True
        email = 'fake@email.com'

        # When
        try:
            check_user_is_logged_in_or_email_is_provided(user, email)

        # Then
        except:
            assert False


