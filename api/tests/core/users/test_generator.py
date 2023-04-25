import pytest

import pcapi.core.users.generator as users_generator


pytestmark = pytest.mark.usefixtures("db_session")


class UserGeneratorTest:
    def test_generate_default_user(self):
        user = users_generator.generate_user()

        assert user.isEmailValidated is True
        assert user.age == 18
        assert user.is_beneficiary is False
