from decimal import Decimal

import pytest

from pcapi.core.finance.factories import RecreditFactory
from pcapi.core.finance.models import RecreditType
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.core.users.factories import UserFactory
from pcapi.scripts.two_credits_manipulation.main import recredit_from_previous_deposit_in_previous_account
from pcapi.scripts.two_credits_manipulation.main import (
    substract_from_deposit_because_of_past_expenses_on_another_account,
)
from pcapi.utils.transaction_manager import atomic


@pytest.mark.usefixtures("db_session")
def test_recredit_is_granted() -> None:
    user = BeneficiaryFactory.create()
    previous_deposit_amount = user.deposit.amount

    with atomic():
        recredit_from_previous_deposit_in_previous_account(user.id)

    assert user.deposit.amount == previous_deposit_amount + Decimal("30")


@pytest.mark.usefixtures("db_session")
def test_recredit_is_substracted() -> None:
    author = UserFactory.create()
    user = BeneficiaryFactory.create()
    expected_deposit_amount = user.deposit.amount

    recredit_to_delete = RecreditFactory(
        deposit=user.deposit, recreditType=RecreditType.RECREDIT_17, amount=Decimal("123.45")
    )
    user.deposit.amount += recredit_to_delete.amount

    with atomic():
        substract_from_deposit_because_of_past_expenses_on_another_account(
            user.id, user_id_with_spent_credit=123, author_id=author.id
        )

    assert user.deposit.amount == expected_deposit_amount
