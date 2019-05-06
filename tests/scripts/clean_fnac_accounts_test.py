import pytest

from models import PcObject
from scripts.clean_fnac_accounts import find_all_fnac_darty_users
from tests.conftest import clean_database
from tests.test_utils import create_user


@pytest.mark.standalone
class GetAllFnacUsersTest:
    @clean_database
    def test_retrieves_users_with_email_ending_with_fnac_dot_com(self, app):
        # Given
        user_fnac = create_user(email='toto@fnacdarty.com')
        user_not_fnac = create_user(email='toto@cultura.com')
        PcObject.check_and_save(user_fnac, user_not_fnac)

        # When
        users = find_all_fnac_darty_users()

        # Then
        assert users == [user_fnac]
