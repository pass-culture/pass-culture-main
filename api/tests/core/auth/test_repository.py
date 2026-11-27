import pytest

from pcapi.core.auth import repository
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class CreateSingleSignOnTest:
    def test_creates_sso(self):
        user = users_factories.UserFactory()

        sso = repository.create_single_sign_on(user, "google", "100428144463745704968")

        assert sso.user == user
        assert user.single_sign_ons == [sso]
