from datetime import datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy import sql

import pcapi.core.bookings.conf as bookings_conf
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.models.deposit import Deposit
from pcapi.models.deposit import DepositType
from pcapi.models.payment import Payment
from pcapi.models.payment_status import PaymentStatus
from pcapi.models.payment_status import TransactionStatus

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
        version = bookings_conf.get_current_deposit_version_for_type(DepositType.GRANT_18)
    booking_configuration = bookings_conf.get_limit_configuration_for_type_and_version(DepositType.GRANT_18, version)

    deposit = Deposit(
        version=version,
        type=DepositType.GRANT_18,
        amount=booking_configuration.TOTAL_CAP,
        source=deposit_source,
        user=beneficiary,
        expirationDate=_get_expiration_date(),
    )
    return deposit


def bulk_create_payment_statuses(payment_query, status: TransactionStatus, detail=None):
    sel = payment_query.with_entities(Payment.id, sql.literal(status.name), sql.literal(detail))
    query = sql.insert(PaymentStatus).from_select(["paymentId", "status", "detail"], sel)
    db.session.execute(query)
    db.session.commit()
