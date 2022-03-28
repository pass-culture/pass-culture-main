import datetime
from decimal import Decimal

import pytest

from pcapi.core.educational import exceptions
from pcapi.core.educational import factories
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveOffer
from pcapi.core.educational.models import EducationalDeposit
from pcapi.models import db


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


class CollectiveOfferIsSoldOutTest:
    def test_is_sold_out_property_false(self):
        offer = factories.CollectiveOfferFactory()
        factories.CollectiveStockFactory(collectiveOffer=offer)

        assert not offer.isSoldOut

    def test_offer_property_is_not_sold_out_when_booking_is_cancelled(self):
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock)

        assert not offer.isSoldOut

    def test_offer_property_is_sold_out(self):
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(collectiveStock=stock)

        assert offer.isSoldOut

    def test_offer_property_is_sold_out_when_some_booking_are_cancelled(self):
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(collectiveStock=stock, status=CollectiveBookingStatus.CANCELLED)
        factories.CollectiveBookingFactory(collectiveStock=stock)
        factories.CollectiveBookingFactory(collectiveStock=stock, status=CollectiveBookingStatus.CANCELLED)

        assert offer.isSoldOut

    def test_is_sold_out_query_false(self):
        offer = factories.CollectiveOfferFactory()
        factories.CollectiveStockFactory(collectiveOffer=offer)

        soldout_offer = factories.CollectiveOfferFactory()
        soldout_stock = factories.CollectiveStockFactory(collectiveOffer=soldout_offer)
        factories.CollectiveBookingFactory(collectiveStock=soldout_stock)

        results = db.session.query(CollectiveOffer).filter(CollectiveOffer.isSoldOut.is_(False)).all()

        assert len(results) == 1
        assert results[0].id == offer.id

    def test_offer_query_is_not_sold_out_when_booking_is_cancelled(self):
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock)

        soldout_offer = factories.CollectiveOfferFactory()
        soldout_stock = factories.CollectiveStockFactory(collectiveOffer=soldout_offer)
        factories.CollectiveBookingFactory(collectiveStock=soldout_stock)

        results = db.session.query(CollectiveOffer).filter(CollectiveOffer.isSoldOut.is_(False)).all()

        assert len(results) == 1
        assert results[0].id == offer.id

    def test_offer_query_is_sold_out(self):
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(collectiveStock=stock)

        undsold_offer = factories.CollectiveOfferFactory()
        undsold_stock = factories.CollectiveStockFactory(collectiveOffer=undsold_offer)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=undsold_stock)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=undsold_stock)

        results = db.session.query(CollectiveOffer).filter(CollectiveOffer.isSoldOut.is_(True)).all()

        assert len(results) == 1
        assert results[0].id == offer.id

    def test_offer_query_is_sold_out_when_some_booking_are_cancelled(self):
        offer = factories.CollectiveOfferFactory()
        stock = factories.CollectiveStockFactory(collectiveOffer=offer)
        factories.CollectiveBookingFactory(collectiveStock=stock, status=CollectiveBookingStatus.CANCELLED)
        factories.CollectiveBookingFactory(collectiveStock=stock)
        factories.CollectiveBookingFactory(collectiveStock=stock, status=CollectiveBookingStatus.CANCELLED)

        undsold_offer = factories.CollectiveOfferFactory()
        undsold_stock = factories.CollectiveStockFactory(collectiveOffer=undsold_offer)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=undsold_stock)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=undsold_stock)

        results = db.session.query(CollectiveOffer).filter(CollectiveOffer.isSoldOut.is_(True)).all()

        assert len(results) == 1
        assert results[0].id == offer.id

    def test_offer_query_is_sold_out_on_realistic_case(self):
        offer_1 = factories.CollectiveOfferFactory()
        stock_1 = factories.CollectiveStockFactory(collectiveOffer=offer_1)
        factories.CollectiveBookingFactory(collectiveStock=stock_1, status=CollectiveBookingStatus.CANCELLED)
        factories.CollectiveBookingFactory(collectiveStock=stock_1)
        factories.CollectiveBookingFactory(collectiveStock=stock_1, status=CollectiveBookingStatus.CANCELLED)
        offer_2 = factories.CollectiveOfferFactory()
        stock_2 = factories.CollectiveStockFactory(collectiveOffer=offer_2)
        factories.CollectiveBookingFactory(collectiveStock=stock_2)

        offer_3 = factories.CollectiveOfferFactory()
        stock_3 = factories.CollectiveStockFactory(collectiveOffer=offer_3)
        factories.CollectiveBookingFactory(status=CollectiveBookingStatus.CANCELLED, collectiveStock=stock_3)
        offer_4 = factories.CollectiveOfferFactory()
        factories.CollectiveStockFactory(collectiveOffer=offer_4)

        results = (
            db.session.query(CollectiveOffer)
            .filter(CollectiveOffer.isSoldOut.is_(True))
            .order_by(CollectiveOffer.id)
            .all()
        )

        assert len(results) == 2
        assert results[0].id == offer_1.id
        assert results[1].id == offer_2.id

        results = (
            db.session.query(CollectiveOffer)
            .filter(CollectiveOffer.isSoldOut.is_(False))
            .order_by(CollectiveOffer.id)
            .all()
        )

        assert len(results) == 2
        assert results[0].id == offer_3.id
        assert results[1].id == offer_4.id
