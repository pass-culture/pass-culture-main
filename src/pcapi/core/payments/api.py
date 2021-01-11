import pcapi.core.bookings.conf as bookings_conf
from pcapi.core.users.models import User
from pcapi.models.deposit import Deposit
from pcapi.models.feature import FeatureToggle
from pcapi.repository import feature_queries

from . import exceptions


def create_deposit(beneficiary: User, deposit_source: str) -> Deposit:
    existing_deposits = bool(Deposit.query.filter_by(userId=beneficiary.id).count())
    if existing_deposits:
        raise exceptions.AlreadyActivatedException({"user": ["Cet utilisateur a déjà crédité son pass Culture"]})

    if feature_queries.is_active(FeatureToggle.APPLY_BOOKING_LIMITS_V2):
        version = 2
        amount = bookings_conf.LimitConfigurationV2.TOTAL_CAP
    else:
        version = 1
        amount = bookings_conf.LimitConfigurationV1.TOTAL_CAP
    deposit = Deposit(
        version=version,
        amount=amount,
        source=deposit_source,
        userId=beneficiary.id,
    )
    return deposit
