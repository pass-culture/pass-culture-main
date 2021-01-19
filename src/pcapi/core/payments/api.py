import pcapi.core.bookings.conf as bookings_conf
from pcapi.core.users.models import User
from pcapi.models.deposit import Deposit
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries

from . import exceptions


def create_deposit(beneficiary: User, deposit_source: str, version: int = None) -> Deposit:
    """Create a new deposit for the user if there is no deposit yet.

    The ``version`` argument MUST NOT be used outside (very specific) tests.
    """
    existing_deposits = bool(Deposit.query.filter_by(userId=beneficiary.id).count())
    if existing_deposits:
        raise exceptions.AlreadyActivatedException({"user": ["Cet utilisateur a déjà crédité son pass Culture"]})

    if version is None:
        version = 2 if feature_queries.is_active(FeatureToggle.APPLY_BOOKING_LIMITS_V2) else 1
    booking_configuration = bookings_conf.LIMIT_CONFIGURATIONS[version]
    deposit = Deposit(
        version=version,
        amount=booking_configuration.TOTAL_CAP,
        source=deposit_source,
        user=beneficiary,
    )
    return deposit
