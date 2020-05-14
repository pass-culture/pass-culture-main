import pytest

from domain.user.user import User
from domain.user.user_exceptions import UserDoesntExist
from repository import repository
from infrastructure.repository.user.user_sql_repository import UserSQLRepository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_deposit


class UserSQLRepositoryTest:
    def setup_method(self):
        self.user_sql_repository = UserSQLRepository()

    @clean_database
    def test_should_return_user_with_correct_information(self, app):
        # Given
        user_sql_entity = create_user(idx=12, can_book_free_offers=True, email='john.doe@example.com',
                                      first_name='John', last_name='Doe', departement_code='75')
        create_deposit(user=user_sql_entity, amount=230)
        repository.save(user_sql_entity)

        # When
        user = self.user_sql_repository.find_user_by_id(user_sql_entity.id)

        # Then
        expected_user = User(
            identifier=user_sql_entity.id,
            can_book_free_offers=True,
            email='john.doe@example.com',
            first_name='John',
            last_name='Doe',
            department_code='75',
            wallet_balance=230,
        )
        assert type(user) == User
        assert user.identifier == expected_user.identifier
        assert user.can_book_free_offers == expected_user.can_book_free_offers
        assert user.email == expected_user.email
        assert user.firstName == expected_user.firstName
        assert user.lastName == expected_user.lastName
        assert user.departmentCode == expected_user.departmentCode
        assert user.wallet_balance == expected_user.wallet_balance

    def test_should_raise_user_doesnt_exist_when_user_is_not_found(self):
        # Given
        unknown_id = 999

        # When
        with pytest.raises(UserDoesntExist) as error:
            self.user_sql_repository.find_user_by_id(unknown_id)

        # Then
        assert error.value.errors['userId'] == ['userId ne correspond à aucun user']
