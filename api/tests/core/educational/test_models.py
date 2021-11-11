from decimal import Decimal

import pytest

from pcapi.core.educational import exceptions
from pcapi.core.educational.models import EducationalDeposit


class EducationalDepositTest:
    def test_final_educational_deposit_amounts(self) -> None:
        # When
        educational_deposit = EducationalDeposit(amount=Decimal(1000.00), isFinal=True)

        # Then
        assert educational_deposit.get_amount() == Decimal(1000.00)

    def test_not_final_educational_deposit_amounts(self) -> None:
        # When
        educational_deposit = EducationalDeposit(amount=Decimal(1000.00), isFinal=False)

        # Then
        assert educational_deposit.get_amount() == Decimal(800.00)

    def test_should_raise_insufficient_fund(self) -> None:
        # When
        educational_deposit = EducationalDeposit(amount=Decimal(1000.00), isFinal=True)

        # Then
        with pytest.raises(exceptions.InsufficientFund):
            educational_deposit.check_has_enough_fund(Decimal(1100.00))

    def test_should_raise_insufficient_temporary_fund(self) -> None:
        # When
        educational_deposit = EducationalDeposit(amount=Decimal(1000.00), isFinal=False)

        # Then
        with pytest.raises(exceptions.InsufficientTemporaryFund):
            educational_deposit.check_has_enough_fund(Decimal(900.00))
