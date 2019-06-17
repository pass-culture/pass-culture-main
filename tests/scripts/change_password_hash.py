from unittest.mock import MagicMock

from models import PcObject
from models.db import db
from scripts.change_password_hash import get_all_users_with_non_standard_passwords, set_new_password_for
from tests.conftest import clean_database
from tests.test_utils import create_user


class GetAllUsersWithNonStandardPasswordTest:
    @clean_database
    def test_returns_users_with_password_length_other_than_60(self, app):
        # Given
        normal_user = create_user(email='test1@email.com')
        user_with_non_standard_password = create_user(email='test2@email.com')
        user_with_non_standard_password.password = b'1234567890'
        PcObject.save(normal_user, user_with_non_standard_password)

        # When
        users = get_all_users_with_non_standard_passwords()

        # Then
        assert users == [user_with_non_standard_password]


class SetNewPasswordForTest:
    @clean_database
    def test_should_change_password_of_users_returned_by_get_users(self, app):
        # Given
        normal_password_length = 60

        user1 = create_user(email='test1@email.com')
        user2 = create_user(email='test2@email.com')
        PcObject.save(user1, user2)

        get_users = MagicMock()
        get_users.return_value = [user1, user2]
        old_user_1_password = user1.password
        old_user_2_password = user2.password

        # When
        set_new_password_for(get_users)

        # Then
        db.session.refresh(user1)
        db.session.refresh(user2)
        assert user1.password != old_user_1_password
        assert user2.password != old_user_2_password
        assert len(user1.password) == normal_password_length
        assert len(user2.password) == normal_password_length
