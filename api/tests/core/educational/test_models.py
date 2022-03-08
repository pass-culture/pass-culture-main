import datetime
from decimal import Decimal

import pytest

from pcapi.core.educational import exceptions
from pcapi.core.educational import factories
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import EducationalDeposit


pytestmark = pytest.mark.usefixtures("db_session")


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


class CollectiveStockIsBookableTest:
    def test_not_bookable_if_booking_limit_datetime_has_passed(self):
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        collective_stock = factories.CollectiveStockFactory(bookingLimitDatetime=past)
        assert not collective_stock.isBookable

    def test_not_bookable_if_offerer_is_not_validated(self):
        collective_stock = factories.CollectiveStockFactory(
            collectiveOffer__venue__managingOfferer__validationToken="token"
        )
        assert not collective_stock.isBookable

    def test_not_bookable_if_offerer_is_not_active(self):
        collective_stock = factories.CollectiveStockFactory(
            collectiveOffer__venue__managingOfferer__isActive=False,
        )
        assert not collective_stock.isBookable

    def test_not_bookable_if_venue_is_not_validated(self):
        collective_stock = factories.CollectiveStockFactory(
            collectiveOffer__venue__validationToken="token",
        )
        assert not collective_stock.isBookable

    def test_not_bookable_if_offer_is_not_active(self):
        collective_stock = factories.CollectiveStockFactory(collectiveOffer__isActive=False)
        assert not collective_stock.isBookable

    def test_not_bookable_if_offer_is_event_with_passed_begining_datetime(self):
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        collective_stock = factories.CollectiveStockFactory(beginningDatetime=past)
        assert not collective_stock.isBookable

    def test_not_bookable_if_no_remaining_stock(self):
        collective_stock = factories.CollectiveStockFactory()
        factories.CollectiveBookingFactory(collectiveStock=collective_stock)
        assert not collective_stock.isBookable

    def test_bookable(self):
        collective_stock = factories.CollectiveStockFactory()
        assert collective_stock.isBookable

    def test_bookable_if_booking_is_cancelled(self):
        collective_stock = factories.CollectiveStockFactory()
        factories.CollectiveBookingFactory(collectiveStock=collective_stock, status=CollectiveBookingStatus.CANCELLED)

        assert collective_stock.isBookable
