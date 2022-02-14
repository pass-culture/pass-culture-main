from flask_login.mixins import AnonymousUserMixin
import pytest

from pcapi.core.users.models import User
from pcapi.models.api_errors import ApiErrors
from pcapi.validation.routes.users_authentifications import check_user_is_logged_in_or_email_is_provided


class CheckUserIsLoggedInOrEmailIsProvidedTest:
    def test_raises_an_error_when_no_email_nor_user_logged(self):
        anonymous = AnonymousUserMixin()
        with pytest.raises(ApiErrors) as excinfo:
            check_user_is_logged_in_or_email_is_provided(anonymous, email=None)
        assert excinfo.value.errors["email"] == [
            "Vous devez préciser l'email de l'utilisateur quand vous n'êtes pas connecté(e)"
        ]

    def test_does_not_raise_error_when_email_is_provided(self):
        anonymous = AnonymousUserMixin()
        # The following call should not raise.
        check_user_is_logged_in_or_email_is_provided(anonymous, email="fake@example.com")

    def test_does_not_raise_error_when_user_is_authenticated(self):
        user = User()
        # The following call should not raise.
        check_user_is_logged_in_or_email_is_provided(user, email="fake@example.com")
