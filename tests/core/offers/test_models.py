import datetime

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.bookings.models import BookingStatus
import pcapi.core.offerers.factories as providers_factories
from pcapi.core.offers import factories
from pcapi.core.offers import models
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import OfferStatus
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.core.offers.models import Stock
from pcapi.models.offer_type import ThingType
from pcapi.utils.date import DateTimes


@pytest.mark.usefixtures("db_session")
class OfferDateRangeTest:
    def test_thing_offer(self):
        offer = factories.ThingOfferFactory()
        factories.StockFactory(offer=offer)
        assert offer.dateRange == DateTimes()

    def test_event_offer(self):
        offer = factories.EventOfferFactory()
        first = datetime.datetime.now() + datetime.timedelta(days=1)
        last = datetime.datetime.now() + datetime.timedelta(days=5)
        factories.StockFactory(offer=offer, beginningDatetime=first)
        factories.StockFactory(offer=offer, beginningDatetime=last)
        assert offer.dateRange == DateTimes(first, last)

    def test_single_stock(self):
        offer = factories.EventOfferFactory()
        stock = factories.StockFactory(offer=offer)
        assert offer.dateRange == DateTimes(stock.beginningDatetime, stock.beginningDatetime)

    def test_no_stock(self):
        offer = factories.EventOfferFactory()
        assert offer.dateRange == DateTimes()

    def test_deleted_stock_is_ignored(self):
        offer = factories.EventOfferFactory()
        factories.StockFactory(offer=offer, isSoftDeleted=True)
        assert offer.dateRange == DateTimes()


class OfferIsDigitalTest:
    def test_is_digital(self):
        offer = models.Offer(url="")
        assert not offer.isDigital
        offer.url = "http://example.com/offer"
        assert offer.isDigital


class OfferTypeTest:
    def test_offer_type(self):
        offer = models.Offer(type=str(ThingType.LIVRE_EDITION))
        assert offer.offerType == {
            "conditionalFields": ["author", "isbn"],
            "proLabel": "Livres papier ou numérique, abonnements lecture",
            "appLabel": "Livre ou carte lecture",
            "offlineOnly": False,
            "onlineOnly": False,
            "sublabel": "Lire",
            "description": "S’abonner à un quotidien d’actualité ?"
            " À un hebdomadaire humoristique ? "
            "À un mensuel dédié à la nature ? "
            "Acheter une BD ou un manga ? "
            "Ou tout simplement ce livre dont tout le monde parle ?",
            "value": "ThingType.LIVRE_EDITION",
            "type": "Thing",
            "isActive": True,
            "canExpire": True,
        }


@pytest.mark.usefixtures("db_session")
class OfferHasBookingLimitDatetimesPassedTest:
    def test_with_stock_with_no_booking_limit_datetime(self):
        stock = factories.StockFactory(bookingLimitDatetime=None)
        offer = stock.offer
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        stock = factories.StockFactory(offer=offer, isSoftDeleted=True, bookingLimitDatetime=past)
        assert not offer.hasBookingLimitDatetimesPassed

    def test_with_stocks_with_booking_limit_datetime(self):
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        stock = factories.StockFactory(bookingLimitDatetime=past)
        assert stock.offer.hasBookingLimitDatetimesPassed

    def test_expression_with_stock_with_no_booking_limit_datetime(self):
        stock = factories.StockFactory(bookingLimitDatetime=None)
        offer = stock.offer

        assert Offer.query.filter(Offer.hasBookingLimitDatetimesPassed.is_(True)).all() == []
        assert Offer.query.filter(Offer.hasBookingLimitDatetimesPassed.is_(False)).all() == [offer]

    def test_expression_with_stock_with_booking_limit_datetime_passed(self):
        past = datetime.datetime.now() - datetime.timedelta(days=1)
        stock = factories.StockFactory(bookingLimitDatetime=past)
        offer = stock.offer

        assert Offer.query.filter(Offer.hasBookingLimitDatetimesPassed.is_(True)).all() == [offer]
        assert Offer.query.filter(Offer.hasBookingLimitDatetimesPassed.is_(False)).all() == []

    def test_expression_with_stock_with_booking_limit_datetime_in_the_future(self):
        future = datetime.datetime.now() + datetime.timedelta(days=2)
        stock = factories.StockFactory(bookingLimitDatetime=future)
        offer = stock.offer

        assert Offer.query.filter(Offer.hasBookingLimitDatetimesPassed.is_(True)).all() == []
        assert Offer.query.filter(Offer.hasBookingLimitDatetimesPassed.is_(False)).all() == [offer]

    def test_expression_with_no_stock(self):
        offer = factories.OfferFactory()

        assert Offer.query.filter(Offer.hasBookingLimitDatetimesPassed.is_(True)).all() == []
        assert Offer.query.filter(Offer.hasBookingLimitDatetimesPassed.is_(False)).all() == [offer]

    def test_expression_with_soft_deleted_stock(self):
        past = datetime.datetime.now() - datetime.timedelta(days=2)
        stock = factories.StockFactory(bookingLimitDatetime=past, isSoftDeleted=True)
        offer = stock.offer

        assert Offer.query.filter(Offer.hasBookingLimitDatetimesPassed.is_(True)).all() == []
        assert Offer.query.filter(Offer.hasBookingLimitDatetimesPassed.is_(False)).all() == [offer]


@pytest.mark.usefixtures("db_session")
class OfferActiveMediationTest:
    def test_active_mediation(self):
        mediation1 = factories.MediationFactory()
        offer = mediation1.offer
        mediation2 = factories.MediationFactory(offer=offer)
        assert offer.activeMediation == mediation2

    def test_ignore_inactive_mediations(self):
        mediation = factories.MediationFactory(isActive=False)
        assert mediation.offer.activeMediation is None


@pytest.mark.usefixtures("db_session")
class OfferIsEditableTest:
    def test_editable_if_not_from_provider(self):
        offer = factories.OfferFactory()
        assert offer.isEditable

    def test_editable_if_from_allocine(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider)
        assert offer.isEditable

    def test_not_editabe_if_from_another_provider(self):
        provider = providers_factories.AllocineProviderFactory(localClass="TiteLiveStocks")
        offer = factories.OfferFactory(lastProvider=provider)
        assert not offer.isEditable


@pytest.mark.usefixtures("db_session")
class OfferThumbUrlTest:
    def test_use_mediation(self):
        mediation = factories.MediationFactory(thumbCount=1)
        offer = mediation.offer
        assert offer.thumbUrl.startswith("http")
        assert offer.thumbUrl == mediation.thumbUrl

    def test_use_product(self):
        product = factories.ProductFactory(thumbCount=1)
        offer = factories.OfferFactory(product=product)
        assert offer.thumbUrl.startswith("http")
        assert offer.thumbUrl == product.thumbUrl

    def test_defaults_to_none(self):
        offer = models.Offer()
        assert offer.thumbUrl == None


class OfferCategoryNameForAppTest:
    def test_offer_category(self):
        offer = models.Offer(type=str(ThingType.JEUX_VIDEO))
        assert offer.offer_category_name_for_app == "JEUX_VIDEO"


@pytest.mark.usefixtures("db_session")
class OfferValidationTest:
    def test_factory_object_defaults_to_approved(self):
        offer = factories.OfferFactory()
        assert offer.validation == OfferValidationStatus.APPROVED


@pytest.mark.usefixtures("db_session")
class OfferStatusTest:
    def test_rejected(self):
        rejected_offer = factories.OfferFactory(validation=OfferValidationStatus.REJECTED, isActive=False)

        assert rejected_offer.status == OfferStatus.REJECTED

    def test_expression_rejected(self):
        rejected_offer = factories.OfferFactory(validation=OfferValidationStatus.REJECTED, isActive=False)
        approved_offer = factories.OfferFactory()

        assert Offer.query.filter(Offer.status == OfferStatus.REJECTED.name).all() == [rejected_offer]
        assert Offer.query.filter(Offer.status != OfferStatus.REJECTED.name).all() == [approved_offer]

    def test_pending(self):
        pending_offer = factories.OfferFactory(validation=OfferValidationStatus.PENDING)

        assert pending_offer.status == OfferStatus.PENDING

    def test_expression_pending(self):
        pending_offer = factories.OfferFactory(validation=OfferValidationStatus.PENDING, isActive=False)
        approved_offer = factories.OfferFactory()

        assert Offer.query.filter(Offer.status == OfferStatus.PENDING.name).all() == [pending_offer]
        assert Offer.query.filter(Offer.status != OfferStatus.PENDING.name).all() == [approved_offer]

    def test_active(self):
        stock = factories.StockFactory()
        active_offer = stock.offer

        assert active_offer.status == OfferStatus.ACTIVE

    def test_expression_active(self):
        stock = factories.StockFactory()
        active_offer = stock.offer

        assert Offer.query.filter(Offer.status == OfferStatus.ACTIVE.name).all() == [active_offer]
        assert Offer.query.filter(Offer.status != OfferStatus.ACTIVE.name).all() == []

    def test_inactive(self):
        inactive_offer = factories.OfferFactory(
            validation=OfferValidationStatus.APPROVED, isActive=False, stocks=[factories.StockFactory()]
        )

        assert inactive_offer.status == OfferStatus.INACTIVE

    def test_expression_inactive(self):
        inactive_offer = factories.OfferFactory(validation=OfferValidationStatus.APPROVED, isActive=False)
        approved_offer = factories.OfferFactory()

        assert Offer.query.filter(Offer.status == OfferStatus.INACTIVE.name).all() == [inactive_offer]
        assert Offer.query.filter(Offer.status != OfferStatus.INACTIVE.name).all() == [approved_offer]

    def test_expired(self):
        past = datetime.datetime.now() - datetime.timedelta(days=2)
        expired_stock = factories.StockFactory(bookingLimitDatetime=past)
        expired_offer = factories.OfferFactory(
            validation=OfferValidationStatus.APPROVED,
            isActive=True,
            stocks=[
                expired_stock,
            ],
        )

        assert expired_offer.status == OfferStatus.EXPIRED

    def test_expression_expired(self):
        expired_stock = factories.StockFactory(bookingLimitDatetime=datetime.datetime.utcnow())
        expired_offer = expired_stock.offer
        approved_offer = factories.OfferFactory()

        assert Offer.query.filter(Offer.status == OfferStatus.EXPIRED.name).all() == [expired_offer]
        assert Offer.query.filter(Offer.status != OfferStatus.EXPIRED.name).all() == [approved_offer]

    def test_sold_out(self):
        sold_out_offer = factories.OfferFactory(
            validation=OfferValidationStatus.APPROVED,
            isActive=True,
        )

        assert sold_out_offer.status == OfferStatus.SOLD_OUT

    def test_expression_sold_out(self):
        sold_out_stock = factories.StockFactory(quantity=0)
        sold_out_offer = sold_out_stock.offer
        not_sold_out_stock = factories.StockFactory(quantity=10)
        not_sold_out_offer = not_sold_out_stock.offer

        assert Offer.query.filter(Offer.status == OfferStatus.SOLD_OUT.name).all() == [sold_out_offer]
        assert Offer.query.filter(Offer.status != OfferStatus.SOLD_OUT.name).all() == [not_sold_out_offer]

    def test_expression_sold_out_offer_without_stock(self):
        offer = factories.OfferFactory()

        assert Offer.query.filter(Offer.status == OfferStatus.SOLD_OUT.name).all() == [offer]
        assert Offer.query.filter(Offer.status != OfferStatus.SOLD_OUT.name).count() == 0

    def test_expression_sold_out_offer_with_passed_stock(self):
        past = datetime.datetime.now() - datetime.timedelta(days=2)
        future = datetime.datetime.now() + datetime.timedelta(days=2)
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, quantity=10, beginningDatetime=past, bookingLimitDatetime=past)
        factories.StockFactory(offer=offer, quantity=0, beginningDatetime=future, bookingLimitDatetime=future)

        assert Offer.query.filter(Offer.status == OfferStatus.SOLD_OUT.name).all() == [offer]
        assert Offer.query.filter(Offer.status != OfferStatus.SOLD_OUT.name).count() == 0


@pytest.mark.usefixtures("db_session")
class StockBookingsQuantityTest:
    def test_bookings_quantity_without_bookings(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=None)

        assert Stock.query.filter(Stock.dnBookedQuantity == 0).one() == stock

    def test_bookings_quantity_with_booking(self):
        offer = factories.OfferFactory(product__type=str(ThingType.INSTRUMENT))
        stock = factories.StockFactory(offer=offer, quantity=5)
        BookingFactory(stock=stock)

        assert Stock.query.filter(Stock.dnBookedQuantity == 0).count() == 0
        assert Stock.query.filter(Stock.dnBookedQuantity == 1).one() == stock

    def test_bookings_quantity_with_a_cancelled_booking(self):
        offer = factories.OfferFactory(product__type=str(ThingType.INSTRUMENT))
        stock = factories.StockFactory(offer=offer, quantity=5)
        BookingFactory(stock=stock)
        BookingFactory(stock=stock, isCancelled=True, status=BookingStatus.CANCELLED)

        assert Stock.query.filter(Stock.dnBookedQuantity == 1).one() == stock


@pytest.mark.usefixtures("db_session")
class OfferIsSoldOutTest:
    def test_offer_with_stock_quantity_is_not_sold_out(self):
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, quantity=5)

        assert offer.isSoldOut is False
        assert Offer.query.filter(Offer.isSoldOut.is_(True)).count() == 0
        assert Offer.query.filter(Offer.isSoldOut.is_(False)).all() == [offer]

    def test_offer_with_unlimited_stock_is_not_sold_out(self):
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, quantity=None)

        assert not offer.isSoldOut
        assert Offer.query.filter(Offer.isSoldOut.is_(True)).count() == 0
        assert Offer.query.filter(Offer.isSoldOut.is_(False)).one() == offer

    def test_offer_with_fully_booked_stock(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=1)
        BookingFactory(stock=stock)

        assert offer.isSoldOut
        assert Offer.query.filter(Offer.isSoldOut.is_(True)).one() == offer
        assert Offer.query.filter(Offer.isSoldOut.is_(False)).count() == 0

    def test_offer_without_stocks(self):
        offer = factories.OfferFactory()

        assert offer.isSoldOut
        assert Offer.query.filter(Offer.isSoldOut.is_(True)).one() == offer
        assert Offer.query.filter(Offer.isSoldOut.is_(False)).count() == 0

    def test_offer_with_passed_stock_date(self):
        past = datetime.datetime.now() - datetime.timedelta(days=2)
        stock = factories.StockFactory(quantity=10, beginningDatetime=past)
        offer = stock.offer

        assert offer.isSoldOut
        assert Offer.query.filter(Offer.isSoldOut.is_(True)).one() == offer
        assert Offer.query.filter(Offer.isSoldOut.is_(False)).count() == 0

    def test_offer_with_soft_deleted_stock(self):
        stock = factories.StockFactory(quantity=10, isSoftDeleted=True)
        offer = stock.offer

        assert offer.isSoldOut
        assert Offer.query.filter(Offer.isSoldOut.is_(True)).one() == offer
        assert Offer.query.filter(Offer.isSoldOut.is_(False)).count() == 0


@pytest.mark.usefixtures("db_session")
class StockRemainingQuantityTest:
    def test_stock_with_unlimited_remaining_quantity(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=None)

        assert stock.remainingQuantity == "unlimited"
        assert Offer.query.filter(Stock.remainingQuantity.is_(None)).one() == offer

    def test_stock_with_unlimited_remaining_quantity_after_booking(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=None)

        BookingFactory(stock=stock)

        assert stock.remainingQuantity == "unlimited"
        assert Offer.query.filter(Stock.remainingQuantity.is_(None)).one() == offer

    def test_stock_with_positive_remaining_quantity(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=5)

        assert stock.remainingQuantity == 5
        assert Offer.query.filter(Stock.remainingQuantity == 5).one() == offer

    def test_stock_with_positive_remaining_quantity_after_some_bookings(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=5)

        BookingFactory(stock=stock, quantity=2)

        assert stock.remainingQuantity == 3
        assert Offer.query.filter(Stock.remainingQuantity == 3).one() == offer

    def test_stock_with_zero_remaining_quantity_after_booking(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=1)

        BookingFactory(stock=stock)

        assert stock.remainingQuantity == 0
        assert Offer.query.filter(Stock.remainingQuantity == 0).one() == offer

    def test_stock_with_positive_remaining_quantity_after_cancelled_booking(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=5)

        BookingFactory(stock=stock, isCancelled=True, status=BookingStatus.CANCELLED)

        assert stock.remainingQuantity == 5
        assert Offer.query.filter(Stock.remainingQuantity == 5).one() == offer
