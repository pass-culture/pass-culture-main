from datetime import datetime
from decimal import Decimal

import pytest
from dateutil.relativedelta import relativedelta

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories.subcategories import VOD
from pcapi.core.finance.models import DepositType
from pcapi.core.finance.models import RecreditType
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.core.users.factories import DepositGrantFactory
from pcapi.scripts.transfer_bookings_to_new_deposits.main import main as transfer_bookings
from pcapi.settings import CREDIT_V3_DECREE_DATETIME


@pytest.mark.usefixtures("db_session")
class TransferBookingsTest:
    @pytest.mark.parametrize("booking_status", [BookingStatus.CONFIRMED, BookingStatus.USED])
    def test_booking_is_transferred(self, booking_status):
        before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(weeks=1)
        user = BeneficiaryFactory(age=17, dateCreated=before_decree)
        booking_to_transfer = BookingFactory(user=user, status=BookingStatus.CONFIRMED, dateCreated=before_decree)

        user.deposit.expirationDate = CREDIT_V3_DECREE_DATETIME
        deposit = DepositGrantFactory(user=user, type=DepositType.GRANT_17_18)
        previous_deposit_amount = deposit.amount

        transfer_bookings(not_dry=True, from_id=user.id - 1, batch_size=10)

        assert booking_to_transfer.deposit.type == DepositType.GRANT_17_18
        assert deposit.amount == previous_deposit_amount + booking_to_transfer.total_amount
        assert RecreditType.MANUAL_MODIFICATION in [recredit.recreditType for recredit in deposit.recredits]

    def test_cancelled_booking_is_transferred_if_cancelled_after_underage_credit_expiration(self):
        before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(weeks=1)
        user = BeneficiaryFactory(age=17, dateCreated=before_decree)
        booking_to_transfer = BookingFactory(
            user=user, status=BookingStatus.CANCELLED, dateCreated=before_decree, cancellationDate=datetime.today()
        )

        user.deposit.expirationDate = CREDIT_V3_DECREE_DATETIME
        deposit = DepositGrantFactory(user=user, type=DepositType.GRANT_17_18)
        previous_deposit_amount = deposit.amount

        transfer_bookings(not_dry=True, from_id=user.id - 1, batch_size=10)

        assert booking_to_transfer.deposit.type == DepositType.GRANT_17_18
        assert deposit.amount == previous_deposit_amount + booking_to_transfer.total_amount
        assert RecreditType.MANUAL_MODIFICATION in [recredit.recreditType for recredit in deposit.recredits]

    def test_cancelled_booking_is_not_transferred_if_cancelled_before_underage_credit_expiration(self):
        before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(weeks=1)
        user = BeneficiaryFactory(age=17, dateCreated=before_decree)
        booking_to_transfer = BookingFactory(
            user=user, status=BookingStatus.CANCELLED, dateCreated=before_decree, cancellationDate=before_decree
        )

        user.deposit.expirationDate = CREDIT_V3_DECREE_DATETIME
        deposit = DepositGrantFactory(user=user, type=DepositType.GRANT_17_18)
        previous_deposit_amount = deposit.amount

        transfer_bookings(not_dry=True, from_id=user.id - 1, batch_size=10)

        assert booking_to_transfer.deposit.type == DepositType.GRANT_15_17
        assert deposit.amount == previous_deposit_amount
        assert RecreditType.MANUAL_MODIFICATION not in [recredit.recreditType for recredit in deposit.recredits]

    def test_reimbursed_booking_is_not_transferred(self):
        before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(weeks=1)
        user = BeneficiaryFactory(age=17, dateCreated=before_decree)
        booking_to_transfer = BookingFactory(user=user, status=BookingStatus.REIMBURSED, dateCreated=before_decree)

        user.deposit.expirationDate = CREDIT_V3_DECREE_DATETIME
        deposit = DepositGrantFactory(user=user, type=DepositType.GRANT_17_18)
        previous_deposit_amount = deposit.amount

        transfer_bookings(not_dry=True, from_id=user.id - 1, batch_size=10)

        assert booking_to_transfer.deposit.type == DepositType.GRANT_15_17
        assert deposit.amount == previous_deposit_amount
        assert RecreditType.MANUAL_MODIFICATION not in [recredit.recreditType for recredit in deposit.recredits]

    def test_not_reimbursed_offer_booking_is_not_transferred(self):
        before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(weeks=1)
        user = BeneficiaryFactory(age=17, dateCreated=before_decree)
        booking_to_transfer = BookingFactory(
            user=user,
            status=BookingStatus.CANCELLED,
            dateCreated=before_decree,
            cancellationDate=before_decree,
            stock__offer__subcategoryId=VOD.id,
        )

        user.deposit.expirationDate = CREDIT_V3_DECREE_DATETIME
        deposit = DepositGrantFactory(user=user, type=DepositType.GRANT_17_18)
        previous_deposit_amount = deposit.amount

        transfer_bookings(not_dry=True, from_id=user.id - 1, batch_size=10)

        assert booking_to_transfer.deposit.type == DepositType.GRANT_15_17
        assert deposit.amount == previous_deposit_amount
        assert RecreditType.MANUAL_MODIFICATION not in [recredit.recreditType for recredit in deposit.recredits]

    def test_free_booking_is_transferred(self):
        before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(weeks=1)
        user = BeneficiaryFactory(age=17, dateCreated=before_decree)
        booking_to_transfer = BookingFactory(
            user=user, status=BookingStatus.CONFIRMED, dateCreated=before_decree, amount=0
        )

        user.deposit.expirationDate = CREDIT_V3_DECREE_DATETIME
        deposit = DepositGrantFactory(user=user, type=DepositType.GRANT_17_18)
        previous_deposit_amount = deposit.amount

        transfer_bookings(not_dry=True, from_id=user.id - 1, batch_size=10)

        assert booking_to_transfer.deposit.type == DepositType.GRANT_15_17
        assert deposit.amount == previous_deposit_amount
        assert RecreditType.MANUAL_MODIFICATION not in [recredit.recreditType for recredit in deposit.recredits]

    @pytest.mark.parametrize("booking_status", [BookingStatus.CONFIRMED, BookingStatus.USED])
    def test_booking_is_not_transferred_for_300_euros_credit(self, booking_status):
        before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(weeks=1)
        user = BeneficiaryFactory(age=17, dateCreated=before_decree)
        booking_to_transfer = BookingFactory(user=user, status=BookingStatus.CONFIRMED, dateCreated=before_decree)

        user.deposit.expirationDate = CREDIT_V3_DECREE_DATETIME
        deposit = DepositGrantFactory(user=user, type=DepositType.GRANT_17_18, amount=Decimal("300"))
        previous_deposit_amount = deposit.amount

        transfer_bookings(not_dry=True, from_id=user.id - 1, batch_size=10)

        assert booking_to_transfer.deposit.type == DepositType.GRANT_15_17
        assert deposit.amount == previous_deposit_amount
        assert RecreditType.MANUAL_MODIFICATION not in [recredit.recreditType for recredit in deposit.recredits]
