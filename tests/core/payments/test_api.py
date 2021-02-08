from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.payments.api import create_deposit
from pcapi.core.users.factories import UserFactory
from pcapi.repository import repository


class CreateDepositTest:
    @freeze_time("2021-02-05 09:00:00")
    @pytest.mark.usefixtures("db_session")
    def test_deposit_created_with_an_expiration_date(self, app):
        # Given
        beneficiary = UserFactory(email="beneficiary@example.com")
        repository.delete(*beneficiary.deposits)

        # When
        deposit = create_deposit(beneficiary, "created by test")

        # Then
        assert deposit.expirationDate == datetime(2023, 2, 5, 9, 0, 0)
