import pytest

from pcapi.core.finance.models import RecreditType
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.scripts.transfer_credit.main import transfer_credit
from pcapi.utils.transaction_manager import atomic


@pytest.mark.usefixtures("db_session")
def test_transfer_credit():
    from_user = BeneficiaryFactory(age=17)
    to_user = BeneficiaryFactory(age=18)
    old_deposit_amount = to_user.deposit.amount

    with atomic():
        transfer_credit(from_user.id, to_user.id)

    assert to_user.deposit.amount == old_deposit_amount + from_user.deposit.amount
    assert RecreditType.MANUAL_MODIFICATION in [recredit.recreditType for recredit in to_user.deposit.recredits]
