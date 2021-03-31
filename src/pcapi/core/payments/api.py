from datetime import datetime

from dateutil.relativedelta import relativedelta

import pcapi.core.bookings.conf as bookings_conf
from pcapi.core.users.models import User
from pcapi.models.deposit import Deposit

from . import exceptions


DEPOSIT_VALIDITY_IN_YEARS = 2


def _get_expiration_date(start=None):
    start = start or datetime.utcnow()
    return start + relativedelta(years=DEPOSIT_VALIDITY_IN_YEARS)


def create_deposit(beneficiary: User, deposit_source: str, version: int = None) -> Deposit:
    """Create a new deposit for the user if there is no deposit yet.

    The ``version`` argument MUST NOT be used outside (very specific) tests.
    """
    existing_deposits = bool(Deposit.query.filter_by(userId=beneficiary.id).count())
    if existing_deposits:
        raise exceptions.AlreadyActivatedException({"user": ["Cet utilisateur a déjà crédité son pass Culture"]})

    if version is None:
        version = bookings_conf.get_current_deposit_version()
    booking_configuration = bookings_conf.LIMIT_CONFIGURATIONS[version]

    deposit = Deposit(
        version=version,
        amount=booking_configuration.TOTAL_CAP,
        source=deposit_source,
        user=beneficiary,
        expirationDate=_get_expiration_date(),
    )
    return deposit
