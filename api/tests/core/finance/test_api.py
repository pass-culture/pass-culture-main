import datetime
from unittest import mock

import pytest
import sqlalchemy.orm as sqla_orm

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
from pcapi.core.finance import api
from pcapi.core.finance import exceptions
from pcapi.core.finance import factories
from pcapi.core.finance import models
import pcapi.core.offers.factories as offers_factories
from pcapi.core.testing import assert_num_queries


pytestmark = pytest.mark.usefixtures("db_session")


def create_booking_with_undeletable_dependent(date_used=None):
    if not date_used:
        date_used = datetime.datetime.utcnow()
    booking = bookings_factories.UsedBookingFactory(dateUsed=date_used)
    business_unit = booking.venue.businessUnit
    factories.PricingFactory(
        businessUnit=business_unit,
        valueDate=booking.dateUsed + datetime.timedelta(seconds=1),
        status=models.PricingStatus.BILLED,
    )
    return booking


class PriceBookingTest:
    def test_basics(self):
        booking = bookings_factories.UsedBookingFactory(
            amount=10,
            stock=offers_factories.ThingStockFactory(),
        )
        pricing = api.price_booking(booking)
        assert models.Pricing.query.count() == 1
        assert pricing.booking == booking
        assert pricing.businessUnit == booking.venue.businessUnit
        assert pricing.valueDate == booking.dateUsed
        assert pricing.amount == -1000
        assert pricing.standardRule == "Remboursement total pour les offres physiques"
        assert pricing.customRule is None
        assert pricing.revenue == 1000

    def test_pricing_lines(self):
        booking1 = bookings_factories.UsedBookingFactory(
            amount=19_999,
            stock=offers_factories.ThingStockFactory(),
        )
        api.price_booking(booking1)
        pricing1 = models.Pricing.query.one()
        assert pricing1.amount == -(19_999 * 100)
        assert pricing1.lines[0].category == models.PricingLineCategory.OFFERER_REVENUE
        assert pricing1.lines[0].amount == -(19_999 * 100)
        assert pricing1.lines[1].category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        assert pricing1.lines[1].amount == 0

        booking2 = bookings_factories.UsedBookingFactory(
            amount=100,
            stock=booking1.stock,
        )
        api.price_booking(booking2)
        pricing2 = models.Pricing.query.filter_by(booking=booking2).one()
        assert pricing2.amount == -(95 * 100)
        assert pricing2.lines[0].category == models.PricingLineCategory.OFFERER_REVENUE
        assert pricing2.lines[0].amount == -(100 * 100)
        assert pricing2.lines[1].category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        assert pricing2.lines[1].amount == 5 * 100

    def test_accrue_revenue(self):
        booking1 = bookings_factories.UsedBookingFactory(amount=10)
        business_unit = booking1.venue.businessUnit
        booking2 = bookings_factories.UsedBookingFactory(
            amount=20,
            stock__offer__venue__businessUnit=business_unit,
        )
        pricing1 = api.price_booking(booking1)
        pricing2 = api.price_booking(booking2)
        assert pricing1.revenue == 1000
        assert pricing2.revenue == 3000

    def test_price_with_dependent_booking(self):
        pricing1 = factories.PricingFactory()
        booking1 = pricing1.booking
        before = booking1.dateUsed - datetime.timedelta(seconds=60)
        booking2 = bookings_factories.UsedBookingFactory(
            dateUsed=before,
            stock__offer__venue__businessUnit=pricing1.businessUnit,
        )
        api.price_booking(booking2)
        # Pricing of `booking1` has been deleted.
        single_princing = models.Pricing.query.one()
        assert single_princing.booking == booking2

    def test_price_booking_that_is_already_priced(self):
        existing = factories.PricingFactory()
        pricing = api.price_booking(existing.booking)
        assert pricing == existing

    def test_price_booking_that_is_not_used(self):
        booking = bookings_factories.BookingFactory()
        pricing = api.price_booking(booking)
        assert pricing is None

    def test_num_queries(self):
        booking = bookings_factories.UsedBookingFactory()
        booking = (
            bookings_models.Booking.query.filter_by(id=booking.id)
            .options(sqla_orm.joinedload(bookings_models.Booking.venue))
            .one()
        )
        queries = 0
        queries += 1  # select for update on BusinessUnit (lock)
        queries += 1  # fetch booking again with multiple joinedload
        queries += 1  # select existing Pricing (if any)
        queries += 1  # select dependent pricings
        queries += 1  # select latest pricing (to get revenue)
        queries += 1  # select all CustomReimbursementRule
        queries += 3  # insert 1 Pricing + 2 PricingLine
        queries += 1  # commit
        with assert_num_queries(queries):
            api.price_booking(booking)


class CancelPricingTest:
    def test_basics(self):
        pricing = factories.PricingFactory()
        reason = models.PricingLogReason.MARK_AS_UNUSED
        pricing = api.cancel_pricing(pricing.booking, reason)
        assert pricing.status == models.PricingStatus.CANCELLED
        assert pricing.logs[0].reason == reason

    def test_cancel_when_no_pricing(self):
        booking = bookings_factories.BookingFactory()
        pricing = api.cancel_pricing(booking, models.PricingLogReason.MARK_AS_UNUSED)
        assert pricing is None

    def test_cancel_when_already_cancelled(self):
        pricing = factories.PricingFactory(status=models.PricingStatus.CANCELLED)
        assert api.cancel_pricing(pricing.booking, models.PricingLogReason.MARK_AS_UNUSED) is None
        assert pricing.status == models.PricingStatus.CANCELLED  # unchanged

    def test_cancel_when_not_cancellable(self):
        pricing = factories.PricingFactory(status=models.PricingStatus.BILLED)
        with pytest.raises(exceptions.NonCancellablePricingError):
            api.cancel_pricing(pricing.booking, models.PricingLogReason.MARK_AS_UNUSED)
        pricing = models.Pricing.query.one()
        assert pricing.status == models.PricingStatus.BILLED  # unchanged

    def test_cancel_with_dependent_booking(self):
        pricing = factories.PricingFactory()
        _dependent_pricing = factories.PricingFactory(
            businessUnit=pricing.businessUnit,
            valueDate=pricing.valueDate + datetime.timedelta(seconds=1),
        )
        pricing = api.cancel_pricing(pricing.booking, models.PricingLogReason.MARK_AS_UNUSED)
        assert pricing.status == models.PricingStatus.CANCELLED
        assert models.Pricing.query.one() == pricing


class DeleteDependentPricingsTest:
    def test_basics(self):
        booking = bookings_factories.UsedBookingFactory()
        business_unit = booking.venue.businessUnit
        earlier_pricing = factories.PricingFactory(
            businessUnit=business_unit,
            valueDate=booking.dateUsed - datetime.timedelta(seconds=1),
        )
        _later_pricing = factories.PricingFactory(
            businessUnit=business_unit,
            valueDate=booking.dateUsed + datetime.timedelta(seconds=1),
        )
        _same_date_pricing_but_greater_booking_id = factories.PricingFactory(
            businessUnit=business_unit,
            valueDate=booking.dateUsed,
        )
        api._delete_dependent_pricings(booking, "some log message")
        assert list(models.Pricing.query.all()) == [earlier_pricing]

    def test_raise_if_a_pricing_is_not_deletable(self):
        booking = create_booking_with_undeletable_dependent()
        pricing = models.Pricing.query.one()
        with pytest.raises(exceptions.NonCancellablePricingError):
            api._delete_dependent_pricings(booking, "some log message")
        assert models.Pricing.query.one() == pricing


class PriceBookingsTest:
    few_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)

    def test_basics(self):
        booking = bookings_factories.UsedBookingFactory(dateUsed=self.few_minutes_ago)
        api.price_bookings()
        assert len(booking.pricings) == 1

    @mock.patch("pcapi.core.finance.api.price_booking", lambda booking: None)
    def test_num_queries(self):
        bookings_factories.UsedBookingFactory(dateUsed=self.few_minutes_ago)
        n_queries = 1
        with assert_num_queries(n_queries):
            api.price_bookings()

    def test_error_on_a_booking_does_not_block_other_bookings(self):
        booking1 = create_booking_with_undeletable_dependent(date_used=self.few_minutes_ago)
        booking2 = bookings_factories.UsedBookingFactory(dateUsed=self.few_minutes_ago)

        api.price_bookings()

        assert not booking1.pricings
        assert len(booking2.pricings) == 1
