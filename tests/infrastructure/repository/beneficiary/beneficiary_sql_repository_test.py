import pytest

from domain.beneficiary.beneficiary import Beneficiary
from domain.beneficiary.beneficiary_exceptions import BeneficiaryDoesntExist
from repository import repository
from infrastructure.repository.beneficiary.beneficiary_sql_repository import BeneficiarySQLRepository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_deposit


class BeneficiarySQLRepositoryTest:
    def setup_method(self):
        self.beneficiary_sql_repository = BeneficiarySQLRepository()

    @clean_database
    def test_should_return_user_with_correct_information(self, app):
        # Given
        beneficiary_sql_entity = create_user(idx=12, can_book_free_offers=True, email='john.doe@example.com',
                                      first_name='John', last_name='Doe', departement_code='75')
        create_deposit(user=beneficiary_sql_entity, amount=230)
        repository.save(beneficiary_sql_entity)

        # When
        user = self.beneficiary_sql_repository.find_beneficiary_by_user_id(beneficiary_sql_entity.id)

        # Then
        expected_user = Beneficiary(
            identifier=beneficiary_sql_entity.id,
            can_book_free_offers=True,
            email='john.doe@example.com',
            first_name='John',
            last_name='Doe',
            department_code='75',
            wallet_balance=230,
        )
        assert type(user) == Beneficiary
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
        with pytest.raises(BeneficiaryDoesntExist) as error:
            self.beneficiary_sql_repository.find_beneficiary_by_user_id(unknown_id)

        # Then
        assert error.value.errors['userId'] == ['userId ne correspond à aucun bénéficiaire']
