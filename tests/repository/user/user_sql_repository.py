import pytest

from domain.user.user import User
from repository import repository
from repository.user.user_sql_repository import UserSQLRepository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user


class UserSQLRepositoryTest:
    def setup_method(self):
        self.user_sql_repository = UserSQLRepository()

    @clean_database
    def test_should_return_user_with_correct_information(self, app):
        # Given
        user_sql_entity = create_user(idx=12, can_book_free_offers=True)
        repository.save(user_sql_entity)

        # When
        user = self.user_sql_repository.find_user_by_id(user_sql_entity.id)

        # Then
        expected_user = User(
            identifier=user_sql_entity.id,
            can_book_free_offers=True,
        )
        assert type(user) == User
        assert user.identifier == expected_user.identifier
        assert user.can_book_free_offers == expected_user.can_book_free_offers

    def test_should_raise_UserDoesntExist_when_user_is_not_found(self):
        # Given
        unknown_id = 999

        # When
        with pytest.raises(UserDoesntExist) as error:
            self.user_sql_repository.find_user_by_id(unknown_id)

        # Then
        assert error.value.errors['userId'] == ['userId ne correspond à aucun user']
