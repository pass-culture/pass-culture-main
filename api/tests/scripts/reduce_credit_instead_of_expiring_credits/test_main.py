import datetime
from decimal import Decimal

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.bookings import factories as bookings_factories
from pcapi.core.users import factories as users_factories
from pcapi.core.users.api import get_domains_credit
from pcapi.scripts.unexpire_credits.main import reduce_credit_instead_of_expiring_credits
from pcapi.utils import transaction_manager


@pytest.mark.usefixtures("db_session")
def test_credit_reduction():
    author = users_factories.UserFactory.create()

    user = users_factories.BeneficiaryFactory.create()
    deposit_amount = user.deposit.amount
    bookings_factories.BookingFactory(user=user, amount=deposit_amount - Decimal("50"))
    user.deposit.expirationDate = datetime.datetime.now(tz=None) - relativedelta(days=1)

    with transaction_manager.atomic():
        reduce_credit_instead_of_expiring_credits([user], should_update_external_user=False, author_id=author.id)

    domains_credit = get_domains_credit(user)
    assert domains_credit.all.remaining == 0
    assert user.has_active_deposit


@pytest.mark.usefixtures("db_session")
def test_credit_partial_reduction():
    author = users_factories.UserFactory.create()

    user = users_factories.BeneficiaryFactory.create()
    deposit_amount = user.deposit.amount
    bookings_factories.BookingFactory(user=user, amount=deposit_amount - Decimal("50.01"))
    user.deposit.expirationDate = datetime.datetime.now(tz=None) - relativedelta(days=1)

    with transaction_manager.atomic():
        reduce_credit_instead_of_expiring_credits([user], should_update_external_user=False, author_id=author.id)

    domains_credit = get_domains_credit(user)
    assert domains_credit.all.remaining == Decimal("0.01")
    assert user.has_active_deposit
