import datetime

import pytest
import time_machine
from sqlalchemy import exc as sa_exc

import pcapi.core.bookings.constants as bookings_constants
import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.providers.factories as providers_factories
from pcapi.core.categories import subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories
from pcapi.core.offers import models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.models.api_errors import ApiErrors
from pcapi.models.validation_status_mixin import ValidationStatus
from pcapi.repository import repository
from pcapi.utils import human_ids


pytestmark = pytest.mark.usefixtures("db_session")


class ProductModelTest:
    def test_thumb_url(self):
        product = factories.ProductFactory(thumbCount=1)
        human_id = human_ids.humanize(product.id)
        assert product.thumbUrl == f"http://localhost/storage/thumbs/products/{human_id}"

    def test_no_thumb_url(self):
        product = models.Product(thumbCount=0)
        assert product.thumbUrl is None

    @pytest.mark.parametrize(
        "gcu_compatible, can_be_synchronized, product_count",
        [
            (models.GcuCompatibilityType.COMPATIBLE, True, 1),
            (models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE, False, 0),
            (models.GcuCompatibilityType.FRAUD_INCOMPATIBLE, False, 0),
        ],
    )
    def test_gcu_compatible(self, gcu_compatible, can_be_synchronized, product_count):
        product = factories.ProductFactory(gcuCompatibilityType=gcu_compatible)

        assert product.can_be_synchronized == can_be_synchronized
        assert db.session.query(models.Product).filter(models.Product.can_be_synchronized).count() == product_count
        db.session.query(models.Product).delete()


class OfferIsDigitalTest:
    def test_is_digital(self):
        offer = models.Offer(url="")
        assert not offer.isDigital
        offer.url = "http://example.com/offer"
        assert offer.isDigital


class OfferHasBookingLimitDatetimesPassedTest:
    def test_with_stock_with_no_booking_limit_datetime(self):
        stock = factories.StockFactory(bookingLimitDatetime=None)
        offer = stock.offer
        past = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        stock = factories.StockFactory(offer=offer, isSoftDeleted=True, bookingLimitDatetime=past)
        assert not offer.hasBookingLimitDatetimesPassed

    def test_with_stocks_with_booking_limit_datetime(self):
        past = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        stock = factories.StockFactory(bookingLimitDatetime=past)
        assert stock.offer.hasBookingLimitDatetimesPassed

    def test_expression_with_stock_with_no_booking_limit_datetime(self):
        stock = factories.StockFactory(bookingLimitDatetime=None)
        offer = stock.offer

        assert db.session.query(models.Offer).filter(models.Offer.hasBookingLimitDatetimesPassed.is_(True)).all() == []
        assert db.session.query(models.Offer).filter(models.Offer.hasBookingLimitDatetimesPassed.is_(False)).all() == [
            offer
        ]

    def test_expression_with_stock_with_booking_limit_datetime_passed(self):
        past = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        stock = factories.StockFactory(bookingLimitDatetime=past)
        offer = stock.offer

        assert db.session.query(models.Offer).filter(models.Offer.hasBookingLimitDatetimesPassed.is_(True)).all() == [
            offer
        ]
        assert db.session.query(models.Offer).filter(models.Offer.hasBookingLimitDatetimesPassed.is_(False)).all() == []

    def test_expression_with_stock_with_booking_limit_datetime_in_the_future(self):
        future = datetime.datetime.utcnow() + datetime.timedelta(days=2)
        stock = factories.StockFactory(bookingLimitDatetime=future)
        offer = stock.offer

        assert db.session.query(models.Offer).filter(models.Offer.hasBookingLimitDatetimesPassed.is_(True)).all() == []
        assert db.session.query(models.Offer).filter(models.Offer.hasBookingLimitDatetimesPassed.is_(False)).all() == [
            offer
        ]

    def test_expression_with_no_stock(self):
        offer = factories.OfferFactory()

        assert db.session.query(models.Offer).filter(models.Offer.hasBookingLimitDatetimesPassed.is_(True)).all() == []
        assert db.session.query(models.Offer).filter(models.Offer.hasBookingLimitDatetimesPassed.is_(False)).all() == [
            offer
        ]

    def test_expression_with_soft_deleted_stock(self):
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        stock = factories.StockFactory(bookingLimitDatetime=past, isSoftDeleted=True)
        offer = stock.offer

        assert db.session.query(models.Offer).filter(models.Offer.hasBookingLimitDatetimesPassed.is_(True)).all() == []
        assert db.session.query(models.Offer).filter(models.Offer.hasBookingLimitDatetimesPassed.is_(False)).all() == [
            offer
        ]


class OfferActiveMediationTest:
    def test_active_mediation(self):
        mediation1 = factories.MediationFactory()
        offer = mediation1.offer
        mediation2 = factories.MediationFactory(offer=offer)
        assert offer.activeMediation == mediation2

    def test_ignore_inactive_mediations(self):
        mediation = factories.MediationFactory(isActive=False)
        assert mediation.offer.activeMediation is None


class OfferIsEditableTest:
    def test_editable_if_not_from_provider(self):
        offer = factories.OfferFactory()
        assert offer.isEditable

    def test_editable_if_from_allocine(self):
        provider = providers_factories.AllocineProviderFactory(localClass="AllocineStocks")
        offer = factories.OfferFactory(lastProvider=provider)
        assert offer.isEditable

    def test_not_editabe_if_from_another_provider(self):
        provider = providers_factories.PublicApiProviderFactory()
        offer = factories.OfferFactory(lastProvider=provider)
        assert not offer.isEditable


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
        assert offer.thumbUrl is None


class OfferValidationTest:
    def test_factory_object_defaults_to_approved(self):
        offer = factories.OfferFactory()
        assert offer.validation == models.OfferValidationStatus.APPROVED


class OfferStatusTest:
    def test_rejected(self):
        rejected_offer = factories.OfferFactory(validation=models.OfferValidationStatus.REJECTED, isActive=False)

        assert rejected_offer.status == offer_mixin.OfferStatus.REJECTED

    def test_expression_rejected(self):
        rejected_offer = factories.OfferFactory(validation=models.OfferValidationStatus.REJECTED, isActive=False)
        approved_offer = factories.OfferFactory()

        assert db.session.query(models.Offer).filter(
            models.Offer.status == offer_mixin.OfferStatus.REJECTED.name
        ).all() == [rejected_offer]
        assert db.session.query(models.Offer).filter(
            models.Offer.status != offer_mixin.OfferStatus.REJECTED.name
        ).all() == [approved_offer]

    def test_pending(self):
        pending_offer = factories.OfferFactory(validation=models.OfferValidationStatus.PENDING)

        assert pending_offer.status == offer_mixin.OfferStatus.PENDING

    def test_expression_pending(self):
        pending_offer = factories.OfferFactory(validation=models.OfferValidationStatus.PENDING, isActive=False)
        approved_offer = factories.OfferFactory()

        assert db.session.query(models.Offer).filter(
            models.Offer.status == offer_mixin.OfferStatus.PENDING.name
        ).all() == [pending_offer]
        assert db.session.query(models.Offer).filter(
            models.Offer.status != offer_mixin.OfferStatus.PENDING.name
        ).all() == [approved_offer]

    def test_active(self):
        stock = factories.StockFactory()
        active_offer = stock.offer

        assert active_offer.status == offer_mixin.OfferStatus.ACTIVE

    def test_expression_active(self):
        stock = factories.StockFactory()
        active_offer = stock.offer

        assert db.session.query(models.Offer).filter(
            models.Offer.status == offer_mixin.OfferStatus.ACTIVE.name
        ).all() == [active_offer]
        assert (
            db.session.query(models.Offer).filter(models.Offer.status != offer_mixin.OfferStatus.ACTIVE.name).all()
            == []
        )

    def test_inactive(self):
        inactive_offer = factories.OfferFactory(
            validation=models.OfferValidationStatus.APPROVED, isActive=False, stocks=[factories.StockFactory()]
        )

        assert inactive_offer.status == offer_mixin.OfferStatus.INACTIVE

    def test_expression_inactive(self):
        inactive_offer = factories.OfferFactory(validation=models.OfferValidationStatus.APPROVED, isActive=False)
        approved_offer = factories.OfferFactory()

        assert db.session.query(models.Offer).filter(
            models.Offer.status == offer_mixin.OfferStatus.INACTIVE.name
        ).all() == [inactive_offer]
        assert db.session.query(models.Offer).filter(
            models.Offer.status != offer_mixin.OfferStatus.INACTIVE.name
        ).all() == [approved_offer]

    def test_expired(self):
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        expired_stock = factories.StockFactory(bookingLimitDatetime=past)
        expired_offer = factories.OfferFactory(
            validation=models.OfferValidationStatus.APPROVED,
            isActive=True,
            stocks=[
                expired_stock,
            ],
        )

        assert expired_offer.status == offer_mixin.OfferStatus.EXPIRED

    def test_expression_expired(self):
        expired_stock = factories.StockFactory(bookingLimitDatetime=datetime.datetime.utcnow())
        expired_offer = expired_stock.offer
        approved_offer = factories.OfferFactory()

        assert db.session.query(models.Offer).filter(
            models.Offer.status == offer_mixin.OfferStatus.EXPIRED.name
        ).all() == [expired_offer]
        assert db.session.query(models.Offer).filter(
            models.Offer.status != offer_mixin.OfferStatus.EXPIRED.name
        ).all() == [approved_offer]

    def test_sold_out(self):
        sold_out_offer = factories.OfferFactory(
            validation=models.OfferValidationStatus.APPROVED,
            isActive=True,
        )

        assert sold_out_offer.status == offer_mixin.OfferStatus.SOLD_OUT

    def test_expression_sold_out(self):
        sold_out_stock = factories.StockFactory(quantity=0)
        sold_out_offer = sold_out_stock.offer
        not_sold_out_stock = factories.StockFactory(quantity=10)
        not_sold_out_offer = not_sold_out_stock.offer

        assert db.session.query(models.Offer).filter(
            models.Offer.status == offer_mixin.OfferStatus.SOLD_OUT.name
        ).all() == [sold_out_offer]
        assert db.session.query(models.Offer).filter(
            models.Offer.status != offer_mixin.OfferStatus.SOLD_OUT.name
        ).all() == [not_sold_out_offer]

    def test_expression_sold_out_offer_without_stock(self):
        offer = factories.OfferFactory()

        assert db.session.query(models.Offer).filter(
            models.Offer.status == offer_mixin.OfferStatus.SOLD_OUT.name
        ).all() == [offer]
        assert (
            db.session.query(models.Offer).filter(models.Offer.status != offer_mixin.OfferStatus.SOLD_OUT.name).count()
            == 0
        )

    def test_expression_sold_out_offer_with_passed_stock(self):
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        future = datetime.datetime.utcnow() + datetime.timedelta(days=2)
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, quantity=10, beginningDatetime=past, bookingLimitDatetime=past)
        factories.StockFactory(offer=offer, quantity=0, beginningDatetime=future, bookingLimitDatetime=future)

        assert db.session.query(models.Offer).filter(
            models.Offer.status == offer_mixin.OfferStatus.SOLD_OUT.name
        ).all() == [offer]
        assert (
            db.session.query(models.Offer).filter(models.Offer.status != offer_mixin.OfferStatus.SOLD_OUT.name).count()
            == 0
        )


class OfferShowSubTypeTest:
    def test_show_sub_type_property(self):
        offer_without_showsubtype = factories.OfferFactory()
        offer_with_showsubtype = factories.OfferFactory(extraData={"showSubType": "1101"})

        assert offer_without_showsubtype.showSubType is None
        assert offer_with_showsubtype.showSubType == "1101"


class StockBookingsQuantityTest:
    def test_bookings_quantity_without_bookings(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=None)

        assert db.session.query(models.Stock).filter(models.Stock.dnBookedQuantity == 0).one() == stock

    def test_bookings_quantity_with_booking(self):
        offer = factories.OfferFactory(subcategoryId=subcategories.ACHAT_INSTRUMENT.id)
        stock = factories.StockFactory(offer=offer, quantity=5)
        bookings_factories.BookingFactory(stock=stock)

        assert db.session.query(models.Stock).filter(models.Stock.dnBookedQuantity == 0).count() == 0
        assert db.session.query(models.Stock).filter(models.Stock.dnBookedQuantity == 1).one() == stock

    def test_bookings_quantity_with_a_cancelled_booking(self):
        offer = factories.OfferFactory(subcategoryId=subcategories.ACHAT_INSTRUMENT.id)
        stock = factories.StockFactory(offer=offer, quantity=5)
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.CancelledBookingFactory(stock=stock)

        assert db.session.query(models.Stock).filter(models.Stock.dnBookedQuantity == 1).one() == stock


class OfferIsSoldOutTest:
    def test_offer_with_stock_quantity_is_not_sold_out(self):
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, quantity=5)

        assert offer.isSoldOut is False
        assert db.session.query(models.Offer).filter(models.Offer.isSoldOut.is_(True)).count() == 0
        assert db.session.query(models.Offer).filter(models.Offer.isSoldOut.is_(False)).all() == [offer]

    def test_offer_with_unlimited_stock_is_not_sold_out(self):
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, quantity=None)

        assert not offer.isSoldOut
        assert db.session.query(models.Offer).filter(models.Offer.isSoldOut.is_(True)).count() == 0
        assert db.session.query(models.Offer).filter(models.Offer.isSoldOut.is_(False)).one() == offer

    def test_offer_with_fully_booked_stock(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=1)
        bookings_factories.BookingFactory(stock=stock)

        assert offer.isSoldOut
        assert db.session.query(models.Offer).filter(models.Offer.isSoldOut.is_(True)).one() == offer
        assert db.session.query(models.Offer).filter(models.Offer.isSoldOut.is_(False)).count() == 0

    def test_offer_without_stocks(self):
        offer = factories.OfferFactory()

        assert offer.isSoldOut
        assert db.session.query(models.Offer).filter(models.Offer.isSoldOut.is_(True)).one() == offer
        assert db.session.query(models.Offer).filter(models.Offer.isSoldOut.is_(False)).count() == 0

    def test_offer_with_passed_stock_date(self):
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        stock = factories.StockFactory(quantity=10, beginningDatetime=past)
        offer = stock.offer

        assert offer.isSoldOut
        assert db.session.query(models.Offer).filter(models.Offer.isSoldOut.is_(True)).one() == offer
        assert db.session.query(models.Offer).filter(models.Offer.isSoldOut.is_(False)).count() == 0

    def test_offer_with_soft_deleted_stock(self):
        stock = factories.StockFactory(quantity=10, isSoftDeleted=True)
        offer = stock.offer

        assert offer.isSoldOut
        assert db.session.query(models.Offer).filter(models.Offer.isSoldOut.is_(True)).one() == offer
        assert db.session.query(models.Offer).filter(models.Offer.isSoldOut.is_(False)).count() == 0


class StockRemainingQuantityTest:
    def test_stock_with_unlimited_remaining_quantity(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=None)

        assert stock.remainingQuantity == "unlimited"
        assert db.session.query(models.Stock).filter(models.Stock.remainingQuantity.is_(None)).one() == stock

    def test_stock_with_unlimited_remaining_quantity_after_booking(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=None)

        bookings_factories.BookingFactory(stock=stock)

        assert stock.remainingQuantity == "unlimited"
        assert db.session.query(models.Stock).filter(models.Stock.remainingQuantity.is_(None)).one() == stock

    def test_stock_with_positive_remaining_quantity(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=5)

        assert stock.remainingQuantity == 5
        assert db.session.query(models.Stock).filter(models.Stock.remainingQuantity == 5).one() == stock

    def test_stock_with_positive_remaining_quantity_after_some_bookings(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=5)

        bookings_factories.BookingFactory(stock=stock, quantity=2)

        assert stock.remainingQuantity == 3
        assert db.session.query(models.Stock).filter(models.Stock.remainingQuantity == 3).one() == stock

    def test_stock_with_zero_remaining_quantity_after_booking(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=1)

        bookings_factories.BookingFactory(stock=stock)

        assert stock.remainingQuantity == 0
        assert db.session.query(models.Stock).filter(models.Stock.remainingQuantity == 0).one() == stock

    def test_stock_with_positive_remaining_quantity_after_cancelled_booking(self):
        offer = factories.OfferFactory()
        stock = factories.StockFactory(offer=offer, quantity=5)

        bookings_factories.CancelledBookingFactory(stock=stock)

        assert stock.remainingQuantity == 5
        assert db.session.query(models.Stock).filter(models.Stock.remainingQuantity == 5).one() == stock


class StockDateModifiedTest:
    def test_update_dateModified_if_quantity_changes(self):
        stock = factories.StockFactory(dateModified=datetime.datetime(2018, 2, 12), quantity=1)
        stock.quantity = 10
        repository.save(stock)
        stock = db.session.query(models.Stock).one()
        assert stock.dateModified.timestamp() == pytest.approx(datetime.datetime.utcnow().timestamp())

    def test_do_not_update_dateModified_if_price_changes(self):
        initial_dt = datetime.datetime(2018, 2, 12)
        stock = factories.StockFactory(dateModified=initial_dt, price=1)
        stock.price = 10
        repository.save(stock)
        stock = db.session.query(models.Stock).one()
        assert stock.dateModified == initial_dt


def test_queryNotSoftDeleted():
    alive = factories.StockFactory()
    deleted = factories.StockFactory(isSoftDeleted=True)
    stocks = models.Stock.queryNotSoftDeleted().all()
    assert len(stocks) == 1
    assert alive in stocks
    assert deleted not in stocks


def test_stock_cannot_have_a_negative_price():
    stock = factories.StockFactory()
    with pytest.raises(ApiErrors) as e:
        stock.price = -10
        repository.save(stock)
    assert e.value.errors["price"] is not None


class StockQuantityTest:
    def test_stock_cannot_have_a_negative_quantity_stock(self):
        stock = factories.StockFactory()
        with pytest.raises(ApiErrors) as e:
            stock.quantity = -4
            repository.save(stock)
        assert e.value.errors["quantity"] == ["La quantité doit être positive."]

    def test_stock_can_have_an_quantity_stock_equal_to_zero(self):
        stock = factories.StockFactory(quantity=0)
        assert stock.quantity == 0

    def test_quantity_update_with_cancellations_exceed_quantity(self):
        # Given
        stock = factories.ThingStockFactory(quantity=2)
        bookings_factories.CancelledBookingFactory(stock=stock)
        bookings_factories.CancelledBookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock)
        bookings_factories.BookingFactory(stock=stock)

        # When
        stock.quantity = 3
        repository.save(stock)

        # Then
        assert db.session.get(models.Stock, stock.id).quantity == 3

    def test_quantity_update_with_more_than_sum_of_bookings(self):
        # Given
        stock = factories.StockFactory(quantity=2)
        bookings_factories.BookingFactory(stock=stock)

        # When
        stock.quantity = 3
        repository.save(stock)

        # Then
        assert db.session.get(models.Stock, stock.id).quantity == 3

    def test_cannot_update_if_less_than_sum_of_bookings(self):
        # Given
        stock = factories.StockFactory(quantity=2)
        bookings_factories.BookingFactory(stock=stock, quantity=2)

        # When
        stock.quantity = 1
        with pytest.raises(ApiErrors) as e:
            repository.save(stock)

        # Then
        assert e.value.errors["quantity"] == ["Le stock total ne peut être inférieur au nombre de réservations"]


class StockIsBookableTest:
    def test_not_bookable_if_booking_limit_datetime_has_passed(self):
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        stock = factories.StockFactory(bookingLimitDatetime=past)
        assert not stock.isBookable

    @pytest.mark.parametrize(
        "validation_status",
        [ValidationStatus.NEW, ValidationStatus.PENDING, ValidationStatus.REJECTED, ValidationStatus.CLOSED],
    )
    def test_not_bookable_if_offerer_is_not_validated(self, validation_status):
        stock = factories.StockFactory(offer__venue__managingOfferer__validationStatus=validation_status)
        assert not stock.isBookable

    def test_not_bookable_if_offerer_is_not_active(self):
        stock = factories.StockFactory(offer__venue__managingOfferer__isActive=False)
        assert not stock.isBookable

    def test_not_bookable_if_offer_is_not_active(self):
        stock = factories.StockFactory(offer__isActive=False)
        assert not stock.isBookable

    def test_not_bookable_if_stock_is_soft_deleted(self):
        stock = factories.StockFactory(isSoftDeleted=True)
        assert not stock.isBookable

    def test_not_bookable_if_offer_is_event_with_passed_begining_datetime(self):
        past = datetime.datetime.utcnow() - datetime.timedelta(days=2)
        stock = factories.EventStockFactory(beginningDatetime=past)
        assert not stock.isBookable

    def test_not_bookable_if_no_remaining_stock(self):
        stock = factories.StockFactory(quantity=1)
        bookings_factories.BookingFactory(stock=stock)
        assert not stock.isBookable

    def test_bookable_if_stock_is_unlimited(self):
        stock = factories.ThingStockFactory(quantity=None)
        bookings_factories.BookingFactory(stock=stock)
        assert stock.isBookable

    def test_bookable(self):
        stock = factories.StockFactory()
        assert stock.isBookable

    def test_is_forbidden_to_underage(self):
        stock = factories.StockFactory(offer__subcategoryId=subcategories.ABO_JEU_VIDEO.id, price=10)

        assert stock.is_forbidden_to_underage

    def test_is_forbidden_to_underage_when_free(self):
        not_free_stock = factories.StockFactory(offer__subcategoryId=subcategories.VISITE_VIRTUELLE.id, price=10)
        free_stock = factories.StockFactory(offer__subcategoryId=subcategories.VISITE_VIRTUELLE.id, price=0)

        assert not_free_stock.is_forbidden_to_underage
        assert not free_stock.is_forbidden_to_underage


class StockIsEventExpiredTest:
    def test_is_not_expired_when_stock_is_not_an_event(self):
        stock = factories.ThingStockFactory()
        assert not stock.isEventExpired

    def test_is_not_expired_when_stock_is_an_event_in_the_future(self):
        future = datetime.datetime.utcnow() + datetime.timedelta(hours=72)
        stock = factories.EventStockFactory(beginningDatetime=future)
        assert not stock.isEventExpired

    def test_is_expired_when_stock_is_an_event_in_the_past(self):
        past = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
        stock = factories.EventStockFactory(beginningDatetime=past)
        assert stock.isEventExpired


class StockIsEventDeletableTest:
    def test_is_deletable_when_stock_is_not_an_event(self):
        stock = factories.ThingStockFactory()
        assert stock.isEventDeletable

    def test_is_deletable_when_stock_is_an_event_in_the_future(self):
        future = datetime.datetime.utcnow() + datetime.timedelta(hours=72)
        stock = factories.EventStockFactory(beginningDatetime=future)
        assert stock.isEventDeletable

    def test_is_deletable_when_stock_is_expired_since_less_than_event_automatic_refund_delay(self):
        dt = datetime.datetime.utcnow() - bookings_constants.AUTO_USE_AFTER_EVENT_TIME_DELAY + datetime.timedelta(1)
        stock = factories.EventStockFactory(beginningDatetime=dt)
        assert stock.isEventDeletable

    def test_is_not_deletable_when_stock_is_expired_since_more_than_event_automatic_refund_delay(self):
        dt = datetime.datetime.utcnow() - bookings_constants.AUTO_USE_AFTER_EVENT_TIME_DELAY
        stock = factories.EventStockFactory(beginningDatetime=dt)
        assert not stock.isEventDeletable

    def test_is_deletable_when_stock_is_expired_since_more_than_event_automatic_refund_delay_but_is_draft(self):
        dt = datetime.datetime.utcnow() - bookings_constants.AUTO_USE_AFTER_EVENT_TIME_DELAY
        stock = factories.EventStockFactory(beginningDatetime=dt, offer__validation=models.OfferValidationStatus.DRAFT)
        assert stock.isEventDeletable


class OfferMinPriceTest:
    def should_be_smallest_stock_price(self):
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, price=5)
        factories.StockFactory(offer=offer, price=10)

        assert offer.min_price == 5

    def should_be_none_when_no_stocks(self):
        offer = factories.OfferFactory()

        assert offer.min_price is None

    def should_be_smallest_stock_price_including_soft_deleted_stocks(self):
        offer = factories.OfferFactory()
        factories.StockFactory(offer=offer, isSoftDeleted=True, price=10)

        assert offer.min_price == 10


class OfferIsActivableTest:
    def test_not_activable_if_status_is_rejected(self):
        rejected_offer = factories.OfferFactory(validation=models.OfferValidationStatus.REJECTED)
        assert not rejected_offer.isActivable

    def test_not_activable_if_no_venue_provider(self):
        inactive_providers = providers_factories.ProviderFactory(isActive=False)
        offer_from_inactive_provider = factories.OfferFactory(
            lastProvider=inactive_providers,
        )
        assert not offer_from_inactive_provider.isActivable

    def test_not_activable_if_venue_provider_is_inactive(self):
        inactive_providers = providers_factories.ProviderFactory(isActive=False)
        inactive_venue_provider = providers_factories.VenueProviderFactory(
            providerId=inactive_providers.id,
            isActive=False,
        )
        offer_from_inactive_venue_provider = factories.OfferFactory(
            lastProvider=inactive_providers,
            venue=inactive_venue_provider.venue,
        )
        assert not offer_from_inactive_venue_provider.isActivable

    def test_offer_is_activable(self):
        active_provider = providers_factories.ProviderFactory()
        active_venue_provider = providers_factories.VenueProviderFactory(
            provider=active_provider,
        )
        offer_from_active_venue_provider = factories.OfferFactory(
            validation=models.OfferValidationStatus.APPROVED,
            lastProvider=active_provider,
            venue=active_venue_provider.venue,
        )
        factories.StockFactory(offer=offer_from_active_venue_provider)
        assert offer_from_active_venue_provider.isActivable

    def test_can_activate_inactive_offer_if_venue_is_active_and_provider_is_not_null(self):
        active_provider = providers_factories.ProviderFactory()
        active_venue_provider = providers_factories.VenueProviderFactory(
            provider=active_provider,
        )
        offer_from_active_venue_provider = factories.OfferFactory(
            validation=models.OfferValidationStatus.APPROVED,
            isActive=False,
            lastProvider=active_provider,
            venue=active_venue_provider.venue,
        )
        factories.StockFactory(offer=offer_from_active_venue_provider)
        assert offer_from_active_venue_provider.isActivable


class OfferfullAddressTest:
    @pytest.mark.parametrize(
        "label,street,expected_full_address",
        [
            ("label", "street of the full address", "label - street of the full address 75000 Paris"),
            (None, "street of the full address", "street of the full address 75000 Paris"),
        ],
    )
    def test_full_address(self, label, street, expected_full_address):
        oa = offerers_factories.OffererAddressFactory(
            label=label,
            address__street=street,
            address__postalCode="75000",
            address__city="Paris",
        )
        offer = factories.OfferFactory(offererAddress=oa)
        assert offer.fullAddress == expected_full_address


class HeadlineOfferTest:
    today = datetime.datetime.utcnow()
    tomorrow = today + datetime.timedelta(days=1)
    day_after_tomorrow = today + datetime.timedelta(days=2)
    next_month = today + datetime.timedelta(days=30)

    def test_headline_offer_is_active(self):
        headline_offer = factories.HeadlineOfferFactory(timespan=(self.today, None))
        assert headline_offer.isActive
        assert (
            db.session.query(models.HeadlineOffer).filter(models.HeadlineOffer.isActive.is_(True)).one()
            == headline_offer
        )
        assert db.session.query(models.HeadlineOffer).filter(models.HeadlineOffer.isActive.is_(False)).first() == None

    def test_headline_offer_with_ending_time_in_the_future_is_active(self):
        headline_offer = factories.HeadlineOfferFactory(timespan=(self.today, self.day_after_tomorrow))
        assert headline_offer.isActive
        assert (
            db.session.query(models.HeadlineOffer).filter(models.HeadlineOffer.isActive.is_(True)).one()
            == headline_offer
        )
        assert db.session.query(models.HeadlineOffer).filter(models.HeadlineOffer.isActive.is_(False)).first() == None

    def test_headline_offer_is_not_active(self):
        headline_offer = factories.HeadlineOfferFactory(timespan=(self.today, self.day_after_tomorrow))
        with time_machine.travel(self.next_month):
            assert not headline_offer.isActive
            # note: it is not possible to test the sql expression here
            # as time_machine affects only python time, not sql's

    def test_headline_offer_without_mediation_is_not_active(self):
        headline_offer = factories.HeadlineOfferFactory(
            timespan=(self.today, self.day_after_tomorrow), without_mediation=True
        )
        assert not headline_offer.isActive
        assert db.session.query(models.HeadlineOffer).filter(models.HeadlineOffer.isActive.is_(True)).first() is None
        assert (
            db.session.query(models.HeadlineOffer).filter(models.HeadlineOffer.isActive.is_(False)).one()
            == headline_offer
        )

    def test_headline_offer_with_product_mediation_is_active(self):
        product = factories.ProductFactory(
            name="Capitale du sud-est",
            description="La cité c'est le sang",
            subcategoryId=subcategories.LIVRE_PAPIER.id,
            gcuCompatibilityType=models.GcuCompatibilityType.COMPATIBLE,
        )
        factories.ProductMediationFactory(product=product, imageType=models.ImageType.RECTO)
        factories.ProductMediationFactory(product=product, imageType=models.ImageType.VERSO)

        offer = factories.OfferFactory(product=product)
        headline_offer = factories.HeadlineOfferFactory(offer=offer, without_mediation=True)

        assert headline_offer.isActive
        assert (
            db.session.query(models.HeadlineOffer).filter(models.HeadlineOffer.isActive.is_(True)).one()
            == headline_offer
        )
        assert db.session.query(models.HeadlineOffer).filter(models.HeadlineOffer.isActive.is_(False)).first() == None

    @pytest.mark.parametrize(
        "timespan,overlaping_timespan",
        [
            ((today, None), (tomorrow, None)),
            ((today, None), (tomorrow, next_month)),
            ((today, day_after_tomorrow), (tomorrow, None)),
            ((today, day_after_tomorrow), (tomorrow, next_month)),
        ],
    )
    def test_unicity_headline_offer(self, timespan, overlaping_timespan):
        offer = factories.OfferFactory(isActive=True)
        factories.HeadlineOfferFactory(offer=offer, timespan=timespan)
        with pytest.raises(sa_exc.IntegrityError):
            factories.HeadlineOfferFactory(offer=offer, timespan=overlaping_timespan)

    def test_unicity_headline_offer_by_venue(self):
        venue = offerers_factories.VenueFactory()
        offer = factories.OfferFactory(isActive=True, venue=venue)
        another_offer_on_the_same_venue = factories.OfferFactory(isActive=True, venue=venue)
        factories.HeadlineOfferFactory(offer=offer)
        with pytest.raises(sa_exc.IntegrityError):
            factories.HeadlineOfferFactory(offer=another_offer_on_the_same_venue)

    def test_new_headline_increments_product_count(self):
        product = factories.ProductFactory()
        factories.HeadlineOfferFactory(offer__product=product)

        assert product.headlinesCount == 1

    def test_headline_deletion_decrements_product_count(self):
        product = factories.ProductFactory()
        headline_offer = factories.HeadlineOfferFactory(offer__product=product)
        assert product.headlinesCount == 1

        db.session.delete(headline_offer)
        db.session.refresh(product)

        assert product.headlinesCount == 0


class OfferIsHeadlineTest:
    today = datetime.datetime.utcnow()
    day_before_yesterday = today - datetime.timedelta(days=2)
    day_after_tomorrow = today + datetime.timedelta(days=2)

    def test_is_headline(self):
        active_headline_offer = factories.HeadlineOfferFactory(timespan=(self.today, self.day_after_tomorrow))
        eternally_active_headline_offer = factories.HeadlineOfferFactory(timespan=(self.today, None))
        inactive_headline_offer = factories.HeadlineOfferFactory(timespan=(self.day_before_yesterday, self.today))
        reactivated_headline_offer = factories.HeadlineOfferFactory(timespan=(self.today, self.day_after_tomorrow))
        factories.HeadlineOfferFactory(
            timespan=(self.day_before_yesterday, self.today), offer=reactivated_headline_offer.offer
        )
        assert active_headline_offer.isActive
        assert not inactive_headline_offer.isActive

        assert active_headline_offer.offer.is_headline_offer
        assert not inactive_headline_offer.offer.is_headline_offer

        assert db.session.query(models.Offer).filter(models.Offer.is_headline_offer.is_(True)).all() == [
            active_headline_offer.offer,
            eternally_active_headline_offer.offer,
            reactivated_headline_offer.offer,
        ]
        assert db.session.query(models.Offer).filter(models.Offer.is_headline_offer.is_(False)).all() == [
            inactive_headline_offer.offer
        ]


class OfferIsSearchableTest:
    def test_offer_is_future(self):
        offer_1 = factories.OfferFactory(isActive=False)
        offer_2 = factories.OfferFactory(isActive=False)
        offer_3 = factories.OfferFactory(isActive=True)
        factories.StockFactory(offer=offer_3)
        future_publication_date = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        past_publication_date = datetime.datetime.utcnow() - datetime.timedelta(days=30)
        factories.FutureOfferFactory(offer=offer_1, publicationDate=future_publication_date)
        factories.FutureOfferFactory(offer=offer_2, publicationDate=past_publication_date)
        factories.FutureOfferFactory(offer=offer_3, publicationDate=future_publication_date)

        assert offer_1.is_eligible_for_search
        assert not offer_2.is_eligible_for_search
        assert offer_3.is_eligible_for_search

        # hybrid property: also check SQL expression
        results = (
            db.session.query(models.Offer.id)
            .outerjoin(models.Stock)
            .outerjoin(models.FutureOffer)
            .filter(models.Offer.is_eligible_for_search)
            .order_by(models.Offer.id)
            .all()
        )
        assert len(results) == 2
        assert results[0].id == offer_1.id
        assert results[1].id == offer_3.id

    def test_offer_is_bookable(self):
        offer_1 = factories.OfferFactory(isActive=True)
        offer_2 = factories.OfferFactory(isActive=False)
        factories.StockFactory(offer=offer_1)

        assert offer_1.is_eligible_for_search
        assert not offer_2.is_eligible_for_search

        # hybrid property: also check SQL expression
        results = (
            db.session.query(models.Offer.id)
            .outerjoin(models.Stock)
            .outerjoin(models.FutureOffer)
            .filter(models.Offer.is_eligible_for_search)
            .all()
        )
        assert len(results) == 1
        assert results[0].id == offer_1.id

    @pytest.mark.parametrize(
        "validation_status,is_eligible_for_search",
        [
            (ValidationStatus.NEW, False),
            (ValidationStatus.PENDING, False),
            (ValidationStatus.VALIDATED, True),
            (ValidationStatus.REJECTED, False),
            (ValidationStatus.CLOSED, False),
        ],
    )
    def test_offerer_validation_status(self, validation_status, is_eligible_for_search):
        offer = factories.OfferFactory(isActive=True, venue__managingOfferer__validationStatus=validation_status)
        factories.StockFactory(offer=offer)

        assert offer.is_eligible_for_search is is_eligible_for_search
