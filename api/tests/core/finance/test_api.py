import csv
import datetime
from decimal import Decimal
import io
import pathlib
from unittest import mock
import zipfile

import pytest
import pytz

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
from pcapi.core.categories import subcategories
import pcapi.core.educational.factories as educational_factories
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import EducationalDepositFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import Ministry
from pcapi.core.finance import api
from pcapi.core.finance import exceptions
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.object_storage.testing import recursive_listdir
import pcapi.core.offerers.api as offerers_api
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import clean_temporary_files
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.models import db
from pcapi.utils import human_ids

import tests


pytestmark = pytest.mark.usefixtures("db_session")


def create_booking_with_undeletable_dependent(date_used=None, **kwargs):
    if not date_used:
        date_used = datetime.datetime.utcnow()
    booking = bookings_factories.UsedBookingFactory(dateUsed=date_used, **kwargs)
    factories.PricingFactory(
        booking__stock__offer__venue=booking.venue,
        valueDate=booking.dateUsed + datetime.timedelta(seconds=1),
        status=models.PricingStatus.PROCESSED,
    )
    return booking


def create_rich_user():
    # create a rich beneficiary who can book the very expensive stocks
    # we have in `invoice_data`.
    user = users_factories.BeneficiaryGrant18Factory()
    user.deposits[0].amount = 100_000
    db.session.add(user.deposits[0])
    db.session.commit()
    return user


def datetime_iterator(first):
    dt = first
    while 1:
        yield dt
        dt += datetime.timedelta(days=15)


class CleanStringTest:
    def test_remove_string_starting_with_space_if_string(self):
        name = " saut de ligne"
        result = api._clean_for_accounting(name)
        assert result == "saut de ligne"

    def test_remove_doublequote_if_string(self):
        name = 'saut de ligne "spécial"\n'
        result = api._clean_for_accounting(name)
        assert result == "saut de ligne spécial"

    def test_remove_new_line_if_string(self):
        name = "saut de ligne\n"
        result = api._clean_for_accounting(name)
        assert result == "saut de ligne"

    def test_remove_new_line_within_string(self):
        name = "saut \n de ligne"
        result = api._clean_for_accounting(name)
        assert result == "saut  de ligne"

    def test_return_value_sent_if_not_string(self):
        number = 1
        result = api._clean_for_accounting(number)
        assert result == 1


def individual_stock_factory(self_, **kwargs):
    create_bank_info = False
    if self_.use_pricing_point and "offer__venue" not in kwargs:
        kwargs.setdefault("offer__venue__pricing_point", "self")
    if getattr(self_, "use_reimbursement_point", False) and "offer__venue" not in kwargs:
        kwargs.setdefault("offer__venue__reimbursement_point", "self")
        create_bank_info = True
    stock = offers_factories.ThingStockFactory(**kwargs)
    if create_bank_info:
        factories.BankInformationFactory(venue=stock.offer.venue)
    return stock


def collective_stock_factory(self_, **kwargs):
    create_bank_info = False
    if self_.use_pricing_point and "offer__venue" not in kwargs:
        kwargs.setdefault("collectiveOffer__venue__pricing_point", "self")
    if getattr(self_, "use_reimbursement_point", False) and "offer__venue" not in kwargs:
        kwargs.setdefault("collectiveOffer__venue__reimbursement_point", "self")
        create_bank_info = True
    stock = educational_factories.CollectiveStockFactory(**kwargs)
    if create_bank_info:
        factories.BankInformationFactory(venue=stock.offer.venue)
    return stock


class PriceBookingTest:
    use_pricing_point = True
    stock_factory = individual_stock_factory

    def test_basics(self):
        booking = bookings_factories.UsedIndividualBookingFactory(
            amount=10,
            stock=self.stock_factory(),
        )
        pricing = api.price_booking(booking, self.use_pricing_point)
        assert models.Pricing.query.count() == 1
        assert pricing.booking == booking
        if self.use_pricing_point:
            assert pricing.pricingPointId == booking.venue.id
        else:
            assert pricing.businessUnit == booking.venue.businessUnit
            assert pricing.siret == booking.venue.siret
        assert pricing.valueDate == booking.dateUsed
        assert pricing.amount == -1000
        assert pricing.standardRule == "Remboursement total pour les offres physiques"
        assert pricing.customRule is None
        assert pricing.revenue == 1000

    def test_pricing_lines(self):
        user = create_rich_user()
        booking1 = bookings_factories.UsedIndividualBookingFactory(
            amount=19_999,
            individualBooking__user=user,
            stock=self.stock_factory(),
        )
        api.price_booking(booking1, self.use_pricing_point)
        pricing1 = models.Pricing.query.one()
        assert pricing1.amount == -(19_999 * 100)
        assert pricing1.lines[0].category == models.PricingLineCategory.OFFERER_REVENUE
        assert pricing1.lines[0].amount == -(19_999 * 100)
        assert pricing1.lines[1].category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        assert pricing1.lines[1].amount == 0

        booking2 = bookings_factories.UsedIndividualBookingFactory(
            amount=100,
            individualBooking__user=user,
            stock=booking1.stock,
        )
        api.price_booking(booking2, self.use_pricing_point)
        pricing2 = models.Pricing.query.filter_by(booking=booking2).one()
        assert pricing2.amount == -(95 * 100)
        assert pricing2.lines[0].category == models.PricingLineCategory.OFFERER_REVENUE
        assert pricing2.lines[0].amount == -(100 * 100)
        assert pricing2.lines[1].category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        assert pricing2.lines[1].amount == 5 * 100

    def test_price_free_booking(self):
        booking = bookings_factories.UsedBookingFactory(
            amount=0,
            stock=self.stock_factory(),
        )
        pricing = api.price_booking(booking, self.use_pricing_point)
        assert models.Pricing.query.count() == 1
        assert pricing.amount == 0

    def test_accrue_revenue(self):
        booking1 = bookings_factories.UsedIndividualBookingFactory(
            amount=10,
            stock=self.stock_factory(),
        )
        booking2 = bookings_factories.UsedEducationalBookingFactory(
            stock=self.stock_factory(offer__venue=booking1.venue),
            amount=20,
        )
        booking3 = bookings_factories.UsedIndividualBookingFactory(
            amount=40,
            stock=self.stock_factory(offer__venue=booking1.venue),
        )
        pricing1 = api.price_booking(booking1, self.use_pricing_point)
        pricing2 = api.price_booking(booking2, self.use_pricing_point)
        pricing3 = api.price_booking(booking3, self.use_pricing_point)
        assert pricing1.revenue == 1000
        assert pricing2.revenue == 1000  # collective booking, not included in revenue
        assert pricing3.revenue == 5000

    def test_price_with_dependent_booking(self):
        booking1 = bookings_factories.UsedBookingFactory(stock=self.stock_factory())
        _pricing1 = factories.PricingFactory(booking=booking1)
        before = booking1.dateUsed - datetime.timedelta(seconds=60)
        booking2 = bookings_factories.UsedBookingFactory(
            dateUsed=before,
            stock=self.stock_factory(offer__venue=booking1.venue),
        )
        api.price_booking(booking2, self.use_pricing_point)
        # Pricing of `booking1` has been deleted.
        single_princing = models.Pricing.query.one()
        assert single_princing.booking == booking2

    def test_price_booking_that_is_already_priced(self):
        booking = bookings_factories.UsedBookingFactory(stock=self.stock_factory())
        existing = factories.PricingFactory(booking=booking)
        pricing = api.price_booking(booking, self.use_pricing_point)
        assert pricing == existing

    def test_price_booking_that_is_not_used(self):
        booking = bookings_factories.BookingFactory()
        pricing = api.price_booking(booking, self.use_pricing_point)
        assert pricing is None

    def test_price_booking_checks_pricing_point(self):
        if not self.use_pricing_point:
            # This test is not relevant when using business units.
            return
        booking = bookings_factories.UsedBookingFactory()
        assert booking.venue.current_pricing_point_id is None
        pricing = api.price_booking(booking, self.use_pricing_point)
        assert pricing is None

    def test_price_booking_checks_business_unit(self):
        if self.use_pricing_point:
            # This test is not relevant when using pricing points.
            return
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue__businessUnit__siret=None)
        pricing = api.price_booking(booking, self.use_pricing_point)
        assert pricing is None

    def test_price_booking_ignores_missing_bank_information(self):
        if self.use_pricing_point:
            # This test is not relevant when using pricing points.
            return
        booking = bookings_factories.UsedBookingFactory(
            stock__offer__venue__businessUnit__bankAccount__status=models.BankInformationStatus.DRAFT,
        )
        pricing = api.price_booking(booking, self.use_pricing_point)
        assert pricing

    def test_num_queries(self):
        booking = bookings_factories.UsedBookingFactory(stock=self.stock_factory())
        window = (booking.dateUsed - datetime.timedelta(days=1), booking.dateUsed + datetime.timedelta(days=1))
        booking = api._get_bookings_to_price(bookings_models.Booking, window, self.use_pricing_point).first()

        queries = 0
        queries += 1  # select for update on BusinessUnit / Venue (lock)
        queries += 1  # fetch booking again with multiple joinedload
        queries += 1  # select existing Pricing (if any)
        queries += 1  # select dependent pricings
        queries += 1  # calculate revenue
        queries += 1  # select all CustomReimbursementRule
        queries += 1  # insert 1 Pricing
        queries += 1  # insert 2 PricingLine
        queries += 1  # commit
        with assert_num_queries(queries):
            api.price_booking(booking, self.use_pricing_point)


class LegacyPriceBookingTest(PriceBookingTest):
    use_pricing_point = False


class PriceCollectiveBookingTest:
    use_pricing_point = True
    stock_factory = collective_stock_factory

    def test_basics(self):
        collective_booking = UsedCollectiveBookingFactory(collectiveStock=self.stock_factory(price=10))
        pricing = api.price_booking(collective_booking, self.use_pricing_point)
        assert models.Pricing.query.count() == 1
        assert pricing.collectiveBooking == collective_booking
        if self.use_pricing_point:
            assert pricing.pricingPointId == collective_booking.venue.id
        else:
            assert pricing.businessUnit == collective_booking.venue.businessUnit
            assert pricing.siret == collective_booking.venue.siret
        assert pricing.valueDate == collective_booking.dateUsed
        assert pricing.amount == -1000
        assert pricing.standardRule == "Remboursement total pour les offres éducationnelles"
        assert pricing.customRule is None
        assert pricing.revenue == 0

    def test_pricing_lines(self):
        stock = self.stock_factory(price=19_999)
        booking1 = UsedCollectiveBookingFactory(collectiveStock=stock)
        api.price_booking(booking1, self.use_pricing_point)
        pricing1 = models.Pricing.query.one()
        assert pricing1.amount == -(19_999 * 100)
        assert pricing1.lines[0].category == models.PricingLineCategory.OFFERER_REVENUE
        assert pricing1.lines[0].amount == -(19_999 * 100)
        assert pricing1.lines[1].category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        assert pricing1.lines[1].amount == 0

        stock.price = 100
        booking2 = UsedCollectiveBookingFactory(collectiveStock=stock)
        api.price_booking(booking2, self.use_pricing_point)
        pricing2 = models.Pricing.query.filter_by(collectiveBooking=booking2).one()
        assert pricing2.amount == -(100 * 100)
        assert pricing2.lines[0].category == models.PricingLineCategory.OFFERER_REVENUE
        assert pricing2.lines[0].amount == -(100 * 100)
        assert pricing2.lines[1].category == models.PricingLineCategory.OFFERER_CONTRIBUTION
        assert pricing2.lines[1].amount == 0

    def test_price_free_booking(self):
        booking = UsedCollectiveBookingFactory(collectiveStock=self.stock_factory(price=0))
        pricing = api.price_booking(booking, self.use_pricing_point)
        assert models.Pricing.query.count() == 1
        assert pricing.amount == 0

    def test_do_not_accrue_revenue(self):
        booking = UsedCollectiveBookingFactory(collectiveStock=self.stock_factory(price=10))
        pricing = api.price_booking(booking, self.use_pricing_point)
        assert pricing.revenue == 0


class LegacyPriceCollectiveBookingTest(PriceCollectiveBookingTest):
    use_pricing_point = False


class GetRevenuePeriodTest:
    def test_after_midnight(self):
        # Year is 2021 in CET.
        value_date = datetime.datetime(2021, 1, 1, 0, 0)
        period = api._get_revenue_period(value_date)

        start = datetime.datetime(2020, 12, 31, 23, 0, tzinfo=pytz.utc)
        end = datetime.datetime(2021, 12, 31, 22, 59, 59, 999999, tzinfo=pytz.utc)
        assert period == (start, end)

    def test_before_midnight(self):
        # Year is 2022 in CET.
        value_date = datetime.datetime(2021, 12, 31, 23, 30)
        period = api._get_revenue_period(value_date)

        start = datetime.datetime(2021, 12, 31, 23, 0, tzinfo=pytz.utc)
        end = datetime.datetime(2022, 12, 31, 22, 59, 59, 999999, tzinfo=pytz.utc)
        assert period == (start, end)


class GetSiretAndCurrentRevenueTest:
    def test_use_venue_siret(self):
        venue = offerers_factories.VenueFactory(siret="123456")
        booking1 = bookings_factories.UsedIndividualBookingFactory(stock__offer__venue=venue, amount=20)
        _pricing1 = factories.PricingFactory(booking=booking1)
        booking2 = bookings_factories.UsedIndividualBookingFactory(stock__offer__venue=venue)
        _pricing_other = factories.PricingFactory()

        siret, current_revenue = api._get_siret_and_current_revenue(booking2)
        assert siret == "123456"
        assert current_revenue == 2000

    def test_use_business_unit_siret(self):
        venue = offerers_factories.VirtualVenueFactory(siret=None, businessUnit__siret="654321")
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue=venue, amount=20)

        siret, current_revenue = api._get_siret_and_current_revenue(booking)
        assert siret == "654321"
        assert current_revenue == 0

    def test_use_booking_quantity(self):
        venue = offerers_factories.VenueFactory(siret="123456")
        factories.PricingFactory(
            booking__stock__offer__venue=venue,
            booking__amount=10,
            booking__quantity=2,
        )
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue=venue)
        siret, current_revenue = api._get_siret_and_current_revenue(booking)
        assert siret == venue.siret
        assert current_revenue == 2000

    def test_consider_booking_date_used(self):
        in_2020 = datetime.datetime(2020, 7, 1)
        in_2021 = datetime.datetime(2021, 7, 1)
        venue = offerers_factories.VenueFactory()
        _pricing_2020 = factories.PricingFactory(
            siret=venue.siret,
            valueDate=in_2020,
            booking__amount=10,
        )
        _pricing_1_2021 = factories.PricingFactory(
            siret=venue.siret,
            valueDate=in_2021,
            booking__amount=20,
        )
        _pricing_2_2021 = factories.PricingFactory(
            siret=venue.siret,
            valueDate=in_2021,
            booking__amount=40,
        )
        booking = bookings_factories.UsedBookingFactory(
            dateCreated=in_2020,
            dateUsed=in_2021,
            stock__offer__venue=venue,
        )

        siret, current_revenue = api._get_siret_and_current_revenue(booking)
        assert siret == venue.siret
        assert current_revenue == 6000

    def test_handle_duplicate_value_date(self):
        value_date = datetime.datetime.utcnow()
        booking = bookings_factories.UsedBookingFactory()
        siret = booking.venue.siret
        factories.PricingFactory(valueDate=value_date, siret=siret, booking__amount=10)
        factories.PricingFactory(valueDate=value_date, siret=siret, booking__amount=20)
        siret, current_revenue = api._get_siret_and_current_revenue(booking)
        assert current_revenue == 3000


class GetPricingPointIdAndCurrentRevenueTest:
    def test_basics(self):
        pricing_point = offerers_factories.VenueFactory()
        offerer = pricing_point.managingOfferer
        venue = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            pricing_point=pricing_point,
        )
        booking1 = bookings_factories.UsedIndividualBookingFactory(
            stock__offer__venue=venue,
            amount=20,
        )
        _pricing1 = factories.PricingFactory(booking=booking1)
        booking2 = bookings_factories.UsedIndividualBookingFactory(stock__offer__venue=venue)
        _pricing_other = factories.PricingFactory()

        pricing_point_id, current_revenue = api._get_pricing_point_id_and_current_revenue(booking2)
        assert pricing_point_id == pricing_point.id
        assert current_revenue == 2000

    def test_use_booking_quantity(self):
        venue = offerers_factories.VenueFactory(pricing_point="self")
        factories.PricingFactory(
            booking__stock__offer__venue=venue,
            booking__amount=20,
            booking__quantity=2,
        )
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue=venue)
        pricing_point_id, current_revenue = api._get_pricing_point_id_and_current_revenue(booking)
        assert pricing_point_id == venue.id
        assert current_revenue == 4000

    def test_consider_booking_date_used(self):
        in_2020 = datetime.datetime(2020, 7, 1)
        in_2021 = datetime.datetime(2021, 7, 1)
        venue = offerers_factories.VenueFactory(pricing_point="self")
        _pricing_2020 = factories.PricingFactory(
            booking__stock__offer__venue=venue,
            valueDate=in_2020,
            booking__amount=10,
        )
        _pricing_1_2021 = factories.PricingFactory(
            booking__stock__offer__venue=venue,
            valueDate=in_2021,
            booking__amount=20,
        )
        _pricing_2_2021 = factories.PricingFactory(
            booking__stock__offer__venue=venue,
            valueDate=in_2021,
            booking__amount=40,
        )
        booking = bookings_factories.UsedBookingFactory(
            stock__offer__venue=venue,
            dateCreated=in_2020,
            dateUsed=in_2021,
        )

        pricing_point_id, current_revenue = api._get_pricing_point_id_and_current_revenue(booking)
        assert pricing_point_id == venue.id
        assert current_revenue == 6000

    def test_handle_duplicate_value_date(self):
        # Check that we're not trying to be too clever in the
        # implementation. See commit 8e5b7c9e688 for further details.
        value_date = datetime.datetime.utcnow()
        venue = offerers_factories.VenueFactory(pricing_point="self")
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue=venue)
        for amount in (10, 20):
            factories.PricingFactory(
                valueDate=value_date,
                booking__amount=amount,
                booking__stock__offer__venue=venue,
            )
        pricing_point_id, current_revenue = api._get_pricing_point_id_and_current_revenue(booking)
        assert pricing_point_id == venue.id
        assert current_revenue == 3000


def auto_override_features(test_method):
    """Override pricing point and reimbursement-point-related feature
    flags for this test method, based on the value of the
    `use_pricing_point` / `use_reimbursement_point` attribute of its
    test class.
    """

    def wrapper(self_, *args, **kwargs):
        active = getattr(self_, "use_pricing_point", False) or getattr(self_, "use_reimbursement_point", False)
        with override_features(
            USE_PRICING_POINT_FOR_PRICING=active,
            USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS=active,
        ):
            return test_method(self_, *args, **kwargs)

    return wrapper


class CancelPricingTest:
    use_pricing_point = True
    stock_factory = individual_stock_factory

    @auto_override_features
    def test_basics(self):
        pricing = factories.PricingFactory(booking__stock=self.stock_factory())
        reason = models.PricingLogReason.MARK_AS_UNUSED
        pricing = api.cancel_pricing(pricing.booking, reason)
        assert pricing.status == models.PricingStatus.CANCELLED
        assert pricing.logs[0].reason == reason

    @auto_override_features
    def test_cancel_when_no_pricing(self):
        booking = bookings_factories.BookingFactory(stock=self.stock_factory())
        pricing = api.cancel_pricing(booking, models.PricingLogReason.MARK_AS_UNUSED)
        assert pricing is None

    @auto_override_features
    def test_cancel_when_already_cancelled(self):
        pricing = factories.PricingFactory(
            booking__stock=self.stock_factory(),
            status=models.PricingStatus.CANCELLED,
        )
        assert api.cancel_pricing(pricing.booking, models.PricingLogReason.MARK_AS_UNUSED) is None
        assert pricing.status == models.PricingStatus.CANCELLED  # unchanged

    @auto_override_features
    def test_cancel_when_not_cancellable(self):
        pricing = factories.PricingFactory(
            booking__stock=self.stock_factory(),
            status=models.PricingStatus.PROCESSED,
        )
        with pytest.raises(exceptions.NonCancellablePricingError):
            api.cancel_pricing(pricing.booking, models.PricingLogReason.MARK_AS_UNUSED)
        pricing = models.Pricing.query.one()
        assert pricing.status == models.PricingStatus.PROCESSED  # unchanged

    @auto_override_features
    def test_cancel_with_dependent_booking(self):
        booking = bookings_factories.UsedBookingFactory(stock=self.stock_factory())
        pricing = factories.PricingFactory(booking=booking)
        _dependent_pricing = factories.PricingFactory(
            booking__stock__offer__venue=booking.venue,
            valueDate=pricing.valueDate + datetime.timedelta(seconds=1),
        )
        pricing = api.cancel_pricing(booking, models.PricingLogReason.MARK_AS_UNUSED)
        assert pricing.status == models.PricingStatus.CANCELLED
        assert models.Pricing.query.one() == pricing


class LegacyCancelPricingTest(CancelPricingTest):
    use_pricing_point = False


class CancelCollectivePricingTest:
    use_pricing_point = True
    stock_factory = collective_stock_factory

    @auto_override_features
    def test_basics(self):
        pricing = factories.CollectivePricingFactory(collectiveBooking__collectiveStock=self.stock_factory())
        reason = models.PricingLogReason.MARK_AS_UNUSED
        pricing = api.cancel_pricing(pricing.collectiveBooking, reason)
        assert pricing.status == models.PricingStatus.CANCELLED
        assert pricing.logs[0].reason == reason

    @auto_override_features
    def test_cancel_when_no_pricing(self):
        booking = CollectiveBookingFactory(collectiveStock=self.stock_factory())
        pricing = api.cancel_pricing(booking, models.PricingLogReason.MARK_AS_UNUSED)
        assert pricing is None

    @auto_override_features
    def test_cancel_when_already_cancelled(self):
        pricing = factories.CollectivePricingFactory(
            status=models.PricingStatus.CANCELLED,
            collectiveBooking__collectiveStock=self.stock_factory(),
        )
        assert api.cancel_pricing(pricing.collectiveBooking, models.PricingLogReason.MARK_AS_UNUSED) is None
        assert pricing.status == models.PricingStatus.CANCELLED  # unchanged

    @auto_override_features
    def test_cancel_when_not_cancellable(self):
        pricing = factories.CollectivePricingFactory(
            status=models.PricingStatus.PROCESSED,
            collectiveBooking__collectiveStock=self.stock_factory(),
        )
        with pytest.raises(exceptions.NonCancellablePricingError):
            api.cancel_pricing(pricing.collectiveBooking, models.PricingLogReason.MARK_AS_UNUSED)
        pricing = models.Pricing.query.one()
        assert pricing.status == models.PricingStatus.PROCESSED  # unchanged


class LegacyCancelCollectivePricingTest(CancelCollectivePricingTest):
    use_pricing_point = False


class DeleteDependentPricingsTest:
    @override_features(USE_PRICING_POINT_FOR_PRICING=True)
    def test_basics(self):
        used_date = datetime.datetime(2022, 1, 15)
        booking = bookings_factories.UsedBookingFactory(
            dateUsed=used_date,
            stock__offer__venue__pricing_point="self",
        )
        earlier_pricing = factories.PricingFactory(
            booking__stock__offer__venue=booking.venue,
            booking__dateUsed=booking.dateUsed - datetime.timedelta(seconds=1),
        )
        earlier_pricing_previous_year = factories.PricingFactory(
            booking__stock__offer__venue=booking.venue,
            booking__dateUsed=booking.dateUsed - datetime.timedelta(days=365),
            booking__stock__beginningDatetime=booking.dateUsed + datetime.timedelta(seconds=1),
        )
        later_pricing = factories.PricingFactory(
            booking__stock__offer__venue=booking.venue,
            booking__dateUsed=booking.dateUsed + datetime.timedelta(seconds=1),
        )
        later_pricing_another_year = factories.PricingFactory(
            booking__stock__offer__venue=booking.venue,
            booking__dateUsed=used_date + datetime.timedelta(days=365),
        )
        factories.PricingLineFactory(pricing=later_pricing)
        factories.PricingLogFactory(pricing=later_pricing)
        _same_date_pricing_but_greater_booking_id = factories.PricingFactory(
            booking__stock__offer__venue=booking.venue,
            valueDate=booking.dateUsed,
        )
        api._delete_dependent_pricings(booking, "some log message", use_pricing_point=True)
        expected_kept = {earlier_pricing_previous_year, earlier_pricing, later_pricing_another_year}
        assert set(models.Pricing.query.all()) == expected_kept

    @override_features(USE_PRICING_POINT_FOR_PRICING=True)
    def test_scenario1(self):
        # 0. V2 is linked to a BU, V1 is not.
        # 1. B1 is marked as used. It cannot be priced yet.
        # 2. B2 is marked as used. It is priced.
        # 3. V1 is linked to a BU, this makes B1 priceable. B1 should
        #    be priced after B2, even though its used date predates
        #    B2's used date).
        datetimes = datetime_iterator(datetime.datetime(2022, 1, 1))
        v2 = offerers_factories.VenueFactory(pricing_point=None)
        offerer = v2.managingOfferer
        offerers_api.link_venue_to_pricing_point(v2, pricing_point_id=v2.id, timestamp=next(datetimes))
        v1 = offerers_factories.VirtualVenueFactory(pricing_point=None, managingOfferer=offerer)
        b1 = bookings_factories.UsedBookingFactory(stock__offer__venue=v1, dateUsed=next(datetimes))
        b2 = bookings_factories.UsedBookingFactory(stock__offer__venue=v2, dateUsed=next(datetimes))
        offerers_api.link_venue_to_pricing_point(v1, pricing_point_id=v2.id, timestamp=next(datetimes))

        # Suppose that we priced b1 first (which we should not).
        factories.PricingFactory(booking=b1)
        # If we were to price b2 now, that should delete b1's pricing
        # because b2 must be priced before b1.
        api._delete_dependent_pricings(b2, "dummy", use_pricing_point=True)
        assert not b1.pricings

    @override_features(USE_PRICING_POINT_FOR_PRICING=True)
    def test_scenario2(self):
        # 0. Venue has 2 bookings.
        # 1. B1 is a booking for event/stock S1.
        # 2. B2 is a booking for event/stock S2 (which happens after S1).
        # 3. B2 is marked as used before the event date.
        # 4. B1 is also marked used before the event date.
        # 5. S1 happens, B1 can then be invoiced.
        # 6. S2 does not happen, B2 should be cancelled. This should
        #    not have any effect on B1.
        datetimes = datetime_iterator(datetime.datetime(2022, 1, 1))
        venue = offerers_factories.VenueFactory(pricing_point=None)
        offerers_api.link_venue_to_pricing_point(venue, venue.id, next(datetimes))
        b2_used = next(datetimes)
        b1_used = next(datetimes)
        s1_date = next(datetimes)
        s2_date = next(datetimes)
        b1 = bookings_factories.UsedBookingFactory(
            stock__beginningDatetime=s1_date,
            stock__offer__venue=venue,
            dateUsed=b1_used,
        )
        b2 = bookings_factories.UsedBookingFactory(
            stock__beginningDatetime=s2_date,
            stock__offer__venue=venue,
            dateUsed=b2_used,
        )

        # Suppose that we priced b2 first (which we should not).
        factories.PricingFactory(booking=b2)
        # If we were to price b1 now, that should delete b2's pricing
        # because b1 must be priced before b2.
        api._delete_dependent_pricings(b1, "dummy", use_pricing_point=True)
        assert not b2.pricings

    @override_features(USE_PRICING_POINT_FOR_PRICING=True)
    def test_scenario3(self):
        # 0. Venue has 2 bookings.
        # 1. B1 is a booking for a thing.
        # 2. B2 is a booking for an event that happened before B1's used date.
        # 3. But B2 has been marked as used after B1.
        # B2 should be priced after B1.
        datetimes = datetime_iterator(datetime.datetime(2022, 1, 1))
        venue = offerers_factories.VenueFactory(pricing_point=None)
        offerers_api.link_venue_to_pricing_point(venue, venue.id, next(datetimes))
        s2_date = next(datetimes)
        b1_used = next(datetimes)
        b2_used = next(datetimes)
        b1 = bookings_factories.UsedBookingFactory(
            stock__offer__venue=venue,
            dateUsed=b1_used,
        )
        b2 = bookings_factories.UsedBookingFactory(
            stock__beginningDatetime=s2_date,
            stock__offer__venue=venue,
            dateUsed=b2_used,
        )

        # Suppose that we priced b2 first (which we should not).
        factories.PricingFactory(booking=b2)
        # If we were to price b1 now, that should delete b2's pricing
        # because b1 must be priced before b2.
        api._delete_dependent_pricings(b1, "dummy", use_pricing_point=True)
        assert not b2.pricings

    @override_features(USE_PRICING_POINT_FOR_PRICING=True)
    def test_scenario4(self):
        # 0. Venue has 2 bookings.
        # 1. B1 is a booking for E1 (that happens on 15/02).
        # 2. B2 is a booking for E2 (that happens on 20/02).
        # 3. B2 is marked as used on 13/02 (_before_ the event date,
        #    it's allowed).
        # 4. B1 is marked as used on 14/02, _after_ B2 but also before
        #    the event date.
        # 5. On 16/02, a cashflow is generated for B1 only, because
        #    it's the only event that has happened yet.
        # 6. The venue cancels E2. We should be able to cancel B2's
        #    pricing.
        # In other words, B2 should be priced after B1.
        venue = offerers_factories.VenueFactory(pricing_point=None)
        offerers_api.link_venue_to_pricing_point(venue, venue.id, datetime.datetime(2022, 1, 1))
        b1 = bookings_factories.UsedBookingFactory(
            stock__beginningDatetime=datetime.datetime(2022, 2, 15),
            stock__offer__venue=venue,
            dateUsed=datetime.datetime(2022, 2, 14),
        )
        b2 = bookings_factories.UsedBookingFactory(
            stock__beginningDatetime=datetime.datetime(2022, 2, 20),  # after s1
            stock__offer__venue=venue,
            dateUsed=datetime.datetime(2022, 2, 13),  # before b1
        )

        # Suppose that we priced b2 first (which we should not).
        factories.PricingFactory(booking=b2)
        # If we were to price b1 now, that should delete b2's pricing
        # because b1 must be priced before b2.
        api._delete_dependent_pricings(b1, "dummy", use_pricing_point=True)
        assert not b2.pricings

    @override_features(USE_PRICING_POINT_FOR_PRICING=True)
    def test_raise_if_a_pricing_is_not_deletable(self):
        booking = create_booking_with_undeletable_dependent(stock__offer__venue__pricing_point="self")
        pricing = models.Pricing.query.one()
        with pytest.raises(exceptions.NonCancellablePricingError):
            api._delete_dependent_pricings(booking, "some log message", use_pricing_point=True)
        assert models.Pricing.query.one() == pricing

        # With the appropriate setting, don't raise and don't
        # delete the pricing.
        with override_settings(FINANCE_OVERRIDE_PRICING_ORDERING_ON_SIRET_LIST=[booking.venue.siret]):
            api._delete_dependent_pricings(booking, "some log message", use_pricing_point=True)
        assert models.Pricing.query.one() == pricing


class LegacyDeleteDependentPricingsTest:
    def test_basics(self):
        used_date = datetime.datetime(2022, 1, 15)
        booking = bookings_factories.UsedBookingFactory(dateUsed=used_date)
        earlier_pricing = factories.PricingFactory(
            booking__stock__offer__venue=booking.venue,
            booking__dateUsed=booking.dateUsed - datetime.timedelta(seconds=1),
        )
        earlier_pricing_previous_year = factories.PricingFactory(
            booking__stock__offer__venue=booking.venue,
            booking__dateUsed=booking.dateUsed - datetime.timedelta(days=365),
            booking__stock__beginningDatetime=booking.dateUsed + datetime.timedelta(seconds=1),
        )
        later_pricing = factories.PricingFactory(
            booking__stock__offer__venue=booking.venue,
            booking__dateUsed=booking.dateUsed + datetime.timedelta(seconds=1),
        )
        later_pricing_another_year = factories.PricingFactory(
            booking__stock__offer__venue=booking.venue,
            booking__dateUsed=used_date + datetime.timedelta(days=365),
        )
        factories.PricingLineFactory(pricing=later_pricing)
        factories.PricingLogFactory(pricing=later_pricing)
        _same_date_pricing_but_greater_booking_id = factories.PricingFactory(
            booking__stock__offer__venue=booking.venue,
            valueDate=booking.dateUsed,
        )
        api._delete_dependent_pricings(booking, "some log message", use_pricing_point=False)
        expected_kept = {earlier_pricing_previous_year, earlier_pricing, later_pricing_another_year}
        assert set(models.Pricing.query.all()) == expected_kept

    def test_scenario1(self):
        # 0. V2 is linked to a BU, V1 is not.
        # 1. B1 is marked as used. It cannot be priced yet.
        # 2. B2 is marked as used. It is priced.
        # 3. V1 is linked to a BU, this makes B1 priceable. B1 should
        #    be priced after B2, even though its used date predates
        #    B2's used date).
        datetimes = datetime_iterator(datetime.datetime(2022, 1, 1))
        v2 = offerers_factories.VenueFactory(businessUnit=None)
        bu = factories.BusinessUnitFactory(siret=v2.siret)
        offerers_api.set_business_unit_to_venue_id(bu.id, v2.id, next(datetimes))
        v1 = offerers_factories.VirtualVenueFactory(businessUnit=None)
        b1 = bookings_factories.UsedBookingFactory(stock__offer__venue=v1, dateUsed=next(datetimes))
        b2 = bookings_factories.UsedBookingFactory(stock__offer__venue=v2, dateUsed=next(datetimes))
        offerers_api.set_business_unit_to_venue_id(bu.id, v1.id, next(datetimes))

        # Suppose that we priced b1 first (which we should not).
        factories.PricingFactory(booking=b1)
        # If we were to price b2 now, that should delete b1's pricing
        # because b2 must be priced before b1.
        api._delete_dependent_pricings(b2, "dummy", use_pricing_point=False)
        assert not b1.pricings

    def test_scenario2(self):
        # 0. Venue has 2 bookings.
        # 1. B1 is a booking for event/stock S1.
        # 2. B2 is a booking for event/stock S2 (which happens after S1).
        # 3. B2 is marked as used before the event date.
        # 4. B1 is also marked used before the event date.
        # 5. S1 happens, B1 can then be invoiced.
        # 6. S2 does not happen, B2 should be cancelled. This should
        #    not have any effect on B1.
        datetimes = datetime_iterator(datetime.datetime(2022, 1, 1))
        venue = offerers_factories.VenueFactory(businessUnit=None)
        bu = factories.BusinessUnitFactory(siret=venue.siret)
        offerers_api.set_business_unit_to_venue_id(bu.id, venue.id, next(datetimes))
        b2_used = next(datetimes)
        b1_used = next(datetimes)
        s1_date = next(datetimes)
        s2_date = next(datetimes)
        b1 = bookings_factories.UsedBookingFactory(
            stock__beginningDatetime=s1_date,
            stock__offer__venue=venue,
            dateUsed=b1_used,
        )
        b2 = bookings_factories.UsedBookingFactory(
            stock__beginningDatetime=s2_date,
            stock__offer__venue=venue,
            dateUsed=b2_used,
        )

        # Suppose that we priced b2 first (which we should not).
        factories.PricingFactory(booking=b2)
        # If we were to price b1 now, that should delete b2's pricing
        # because b1 must be priced before b2.
        api._delete_dependent_pricings(b1, "dummy", use_pricing_point=False)
        assert not b2.pricings

    def test_scenario3(self):
        # 0. Venue has 2 bookings.
        # 1. B1 is a booking for a thing.
        # 2. B2 is a booking for an event that happened before B1's used date.
        # 3. But B2 has been marked as used after B1.
        # B2 should be priced after B1.
        datetimes = datetime_iterator(datetime.datetime(2022, 1, 1))
        venue = offerers_factories.VenueFactory(businessUnit=None)
        bu = factories.BusinessUnitFactory(siret=venue.siret)
        offerers_api.set_business_unit_to_venue_id(bu.id, venue.id, next(datetimes))
        s2_date = next(datetimes)
        b1_used = next(datetimes)
        b2_used = next(datetimes)
        b1 = bookings_factories.UsedBookingFactory(
            stock__offer__venue=venue,
            dateUsed=b1_used,
        )
        b2 = bookings_factories.UsedBookingFactory(
            stock__beginningDatetime=s2_date,
            stock__offer__venue=venue,
            dateUsed=b2_used,
        )

        # Suppose that we priced b2 first (which we should not).
        factories.PricingFactory(booking=b2)
        # If we were to price b1 now, that should delete b2's pricing
        # because b1 must be priced before b2.
        api._delete_dependent_pricings(b1, "dummy", use_pricing_point=False)
        assert not b2.pricings

    def test_scenario4(self):
        # 0. Venue has 2 bookings.
        # 1. B1 is a booking for E1 (that happens on 15/02).
        # 2. B2 is a booking for E2 (that happens on 20/02).
        # 3. B2 is marked as used on 13/02 (_before_ the event date,
        #    it's allowed).
        # 4. B1 is marked as used on 14/02, _after_ B2 but also before
        #    the event date.
        # 5. On 16/02, a cashflow is generated for B1 only, because
        #    it's the only event that has happened yet.
        # 6. The venue cancels E2. We should be able to cancel B2's
        #    pricing.
        # In other words, B2 should be priced after B1.
        venue = offerers_factories.VenueFactory(businessUnit=None)
        bu = factories.BusinessUnitFactory(siret=venue.siret)
        offerers_api.set_business_unit_to_venue_id(bu.id, venue.id, datetime.datetime(2022, 1, 1))
        b1 = bookings_factories.UsedBookingFactory(
            stock__beginningDatetime=datetime.datetime(2022, 2, 15),
            stock__offer__venue=venue,
            dateUsed=datetime.datetime(2022, 2, 14),
        )
        b2 = bookings_factories.UsedBookingFactory(
            stock__beginningDatetime=datetime.datetime(2022, 2, 20),  # after s1
            stock__offer__venue=venue,
            dateUsed=datetime.datetime(2022, 2, 13),  # before b1
        )

        # Suppose that we priced b2 first (which we should not).
        factories.PricingFactory(booking=b2)
        # If we were to price b1 now, that should delete b2's pricing
        # because b1 must be priced before b2.
        api._delete_dependent_pricings(b1, "dummy", use_pricing_point=False)
        assert not b2.pricings

    def test_raise_if_a_pricing_is_not_deletable(self):
        booking = create_booking_with_undeletable_dependent()
        pricing = models.Pricing.query.one()
        with pytest.raises(exceptions.NonCancellablePricingError):
            api._delete_dependent_pricings(booking, "some log message", use_pricing_point=False)
        assert models.Pricing.query.one() == pricing

        # With the appropriate setting, don't raise and don't
        # delete the pricing.
        with override_settings(FINANCE_OVERRIDE_PRICING_ORDERING_ON_SIRET_LIST=[booking.venue.siret]):
            api._delete_dependent_pricings(booking, "some log message", use_pricing_point=False)
        assert models.Pricing.query.one() == pricing


class PriceBookingsTest:
    few_minutes_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
    use_pricing_point = True
    individual_stock_factory = individual_stock_factory
    collective_stock_factory = collective_stock_factory

    @auto_override_features
    def test_basics(self):
        booking = bookings_factories.UsedBookingFactory(
            dateUsed=self.few_minutes_ago,
            stock=self.individual_stock_factory(),
        )
        educational_booking = bookings_factories.UsedEducationalBookingFactory(dateUsed=self.few_minutes_ago)
        collective_booking = UsedCollectiveBookingFactory(
            dateUsed=self.few_minutes_ago,
            collectiveStock=self.collective_stock_factory(),
        )
        api.price_bookings(min_date=self.few_minutes_ago)
        assert len(booking.pricings) == 1
        assert len(educational_booking.pricings) == 0
        assert len(collective_booking.pricings) == 1

    @auto_override_features
    def test_loop(self):
        bookings_factories.UsedBookingFactory(
            id=2,
            dateUsed=self.few_minutes_ago - datetime.timedelta(minutes=1),
            stock=self.individual_stock_factory(),
        )
        bookings_factories.UsedBookingFactory(
            id=1,
            dateUsed=self.few_minutes_ago,
            stock=self.individual_stock_factory(),
        )
        UsedCollectiveBookingFactory.create_batch(
            3,
            dateUsed=self.few_minutes_ago,
            collectiveStock=self.collective_stock_factory(),
        )
        api.price_bookings(
            min_date=self.few_minutes_ago - datetime.timedelta(minutes=1),
            batch_size=1,
        )
        assert models.Pricing.query.count() == 2 + 3

    @auto_override_features
    @mock.patch("pcapi.core.finance.api.price_booking", lambda booking, use_pricing_point: None)
    def test_num_queries(self):
        bookings_factories.UsedBookingFactory(
            dateUsed=self.few_minutes_ago,
            stock=self.individual_stock_factory(),
        )
        educational_factories.UsedCollectiveBookingFactory(
            dateUsed=self.few_minutes_ago,
            collectiveStock=self.collective_stock_factory(),
        )
        n_queries = 1  # fetch `USE_PRICING_POINT_FOR_PRICING` feature flag
        n_queries += 1  # count of individual bookings to price
        n_queries += 1  # count of collective bookings to price
        n_queries += 1  # select individual bookings
        n_queries += 1  # select collective bookings
        with assert_num_queries(n_queries):
            api.price_bookings(self.few_minutes_ago)

    @auto_override_features
    def test_error_on_a_booking_does_not_block_other_bookings(self):
        booking1 = create_booking_with_undeletable_dependent(
            date_used=self.few_minutes_ago,
            stock=self.individual_stock_factory(),
        )
        booking2 = bookings_factories.UsedBookingFactory(
            dateUsed=self.few_minutes_ago,
            stock=self.individual_stock_factory(),
        )

        api.price_bookings(self.few_minutes_ago)

        assert not booking1.pricings
        assert len(booking2.pricings) == 1

    @auto_override_features
    def test_price_even_without_accepted_bank_info(self):
        if self.use_pricing_point:
            return  # This test is not relevant when using pricing points.
        booking = bookings_factories.UsedBookingFactory(
            dateUsed=self.few_minutes_ago,
            stock__offer__venue__businessUnit__bankAccount__status=models.BankInformationStatus.DRAFT,
        )
        api.price_bookings(min_date=self.few_minutes_ago)
        assert len(booking.pricings) == 1

    @auto_override_features
    def test_order_on_event_date(self):
        event_day1 = datetime.datetime.utcnow() - datetime.timedelta(days=3)
        event_day2 = datetime.datetime.utcnow() - datetime.timedelta(days=2)

        used_date1 = datetime.datetime.utcnow() - datetime.timedelta(days=10)
        used_date2 = datetime.datetime.utcnow() - datetime.timedelta(days=9)
        used_date3 = datetime.datetime.utcnow() - datetime.timedelta(days=8)
        used_date4 = datetime.datetime.utcnow() - datetime.timedelta(days=7)

        # Use the same venue so that we only consider the event date
        # and the used date.
        venue = offerers_factories.VenueFactory(pricing_point="self")

        booking1 = bookings_factories.UsedBookingFactory(
            # non-event, created first, marked as used first
            dateUsed=used_date1,
            stock__offer__venue=venue,
        )
        booking2 = bookings_factories.UsedBookingFactory(
            # event, marked as used before the event date
            dateUsed=used_date3,
            stock__beginningDatetime=event_day2,
            stock__offer__venue=venue,
        )
        booking3 = bookings_factories.UsedBookingFactory(
            # event, marked as used after booking2, but with an event
            # date *before* booking2 event date.
            dateUsed=used_date4,
            stock__beginningDatetime=event_day1,
            stock__offer__venue=venue,
        )
        booking4 = bookings_factories.UsedBookingFactory(
            # non-event, created last, marked as used second
            dateUsed=used_date2,
            stock__offer__venue=venue,
        )

        api.price_bookings()
        pricings = models.Pricing.query.order_by(models.Pricing.id).all()
        ordered_bookings = [pricing.booking for pricing in pricings]
        assert ordered_bookings == [booking1, booking4, booking3, booking2]

    @auto_override_features
    def test_order_on_pricing_point_venue_link_date(self):
        if not self.use_pricing_point:
            return  # This test is not relevant when using business units.
        venue1 = offerers_factories.VenueFactory(pricing_point=None)
        booking1 = bookings_factories.UsedBookingFactory(
            dateUsed=datetime.datetime.utcnow() - datetime.timedelta(days=2),
            stock__offer__venue=venue1,
        )
        venue2 = offerers_factories.VenueFactory(
            managingOfferer=venue1.managingOfferer,
            pricing_point="self",
        )
        booking2 = bookings_factories.UsedBookingFactory(
            dateUsed=booking1.dateUsed + datetime.timedelta(days=1),
            stock__offer__venue=venue2,
        )

        # booking1 is not priced because its venue is not linked to any pricing point.
        api.price_bookings()
        pricing = models.Pricing.query.one()
        assert pricing.booking == booking2

        # Make booking1 priceable.
        offerers_api.link_venue_to_pricing_point(venue1, pricing_point_id=venue1.id)
        api.price_bookings()

        pricings = models.Pricing.query.all()
        assert {pricing.booking for pricing in pricings} == {booking1, booking2}

    @auto_override_features
    def test_order_on_business_unit_venue_link_date(self):
        if self.use_pricing_point:
            return  # This test is not relevant when using pricing points.
        venue1 = offerers_factories.VenueFactory(businessUnit=None)
        booking1 = bookings_factories.UsedBookingFactory(
            dateUsed=datetime.datetime.utcnow() - datetime.timedelta(days=2),
            stock__offer__venue=venue1,
        )
        venue2 = offerers_factories.VenueFactory()
        booking2 = bookings_factories.UsedBookingFactory(
            dateUsed=booking1.dateUsed + datetime.timedelta(days=1),
            stock__offer__venue=venue2,
        )

        # booking1 is not priced because its venue is not linked to any business unit.
        api.price_bookings()
        pricing = models.Pricing.query.one()
        assert pricing.booking == booking2

        # Make booking1 priceable.
        offerers_api.set_business_unit_to_venue_id(venue2.businessUnitId, venue1.id)
        api.price_bookings()

        pricings = models.Pricing.query.all()
        assert {pricing.booking for pricing in pricings} == {booking1, booking2}


class LegacyPriceBookingsTest(PriceBookingsTest):
    use_pricing_point = False


def test_get_next_cashflow_batch_label():
    label = api._get_next_cashflow_batch_label()
    assert label == "VIR1"

    factories.CashflowBatchFactory(label=label)
    label = api._get_next_cashflow_batch_label()
    assert label == "VIR2"


class GenerateCashflowsTest:
    use_reimbursement_point = True

    @auto_override_features
    def test_basics(self):
        now = datetime.datetime.utcnow()
        reimbursement_point1 = offerers_factories.VenueFactory()
        bank_info1 = factories.BankInformationFactory(venue=reimbursement_point1)
        reimbursement_point2 = offerers_factories.VenueFactory()
        factories.BankInformationFactory(venue=reimbursement_point2)
        pricing11 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue__reimbursement_point=reimbursement_point1,
            amount=-1000,
        )
        pricing12 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            amount=-1000,
            booking__stock__offer__venue__reimbursement_point=reimbursement_point1,
        )
        pricing2 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            amount=-3000,
            booking__stock__beginningDatetime=now - datetime.timedelta(days=1),
            booking__stock__offer__venue__reimbursement_point=reimbursement_point2,
        )
        collective_pricing13 = factories.CollectivePricingFactory(
            status=models.PricingStatus.VALIDATED,
            collectiveBooking__collectiveStock__collectiveOffer__venue__reimbursement_point=reimbursement_point1,
            amount=-500,
            collectiveBooking__collectiveStock__beginningDatetime=now - datetime.timedelta(days=1),
        )
        pricing_future_event = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__beginningDatetime=now + datetime.timedelta(days=1),
            booking__stock__offer__venue__reimbursement_point=reimbursement_point1,
        )
        collective_pricing_future_event = factories.CollectivePricingFactory(
            status=models.PricingStatus.VALIDATED,
            collectiveBooking__collectiveStock__beginningDatetime=now + datetime.timedelta(days=1),
            collectiveBooking__collectiveStock__collectiveOffer__venue__reimbursement_point=reimbursement_point1,
        )
        pricing_pending = factories.PricingFactory(
            status=models.PricingStatus.PENDING,
            booking__stock__offer__venue__reimbursement_point=reimbursement_point1,
        )
        cutoff = datetime.datetime.utcnow()
        pricing_after_cutoff = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue__reimbursement_point=reimbursement_point1,
        )

        batch_id = api.generate_cashflows(cutoff)

        batch = models.CashflowBatch.query.one()
        assert batch.id == batch_id
        assert batch.cutoff == cutoff
        assert pricing11.status == models.PricingStatus.PROCESSED
        assert pricing12.status == models.PricingStatus.PROCESSED
        assert collective_pricing13.status == models.PricingStatus.PROCESSED
        assert pricing2.status == models.PricingStatus.PROCESSED
        assert models.Cashflow.query.count() == 2
        assert len(pricing11.cashflows) == 1
        assert len(pricing12.cashflows) == 1
        assert len(collective_pricing13.cashflows) == 1
        assert pricing11.cashflows == pricing12.cashflows == collective_pricing13.cashflows
        assert len(pricing2.cashflows) == 1
        assert pricing11.cashflows[0].amount == -2500
        assert pricing11.cashflows[0].bankAccount == bank_info1
        assert pricing2.cashflows[0].amount == -3000

        assert not pricing_future_event.cashflows
        assert not collective_pricing_future_event.cashflows
        assert not pricing_pending.cashflows
        assert not pricing_after_cutoff.cashflows

    @auto_override_features
    def test_no_cashflow_if_no_accepted_bank_information(self):
        venue_ok = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(venue=venue_ok)
        venue_rejected_iban = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(
            venue=venue_rejected_iban,
            status=models.BankInformationStatus.REJECTED,
        )
        venue_without_iban = offerers_factories.VenueFactory(reimbursement_point="self")

        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue_ok,
            amount=-1000,
        )
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue_rejected_iban,
            amount=-2000,
        )
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue_without_iban,
            amount=-4000,
        )

        cutoff = datetime.datetime.utcnow()
        api.generate_cashflows(cutoff)

        cashflow = models.Cashflow.query.one()
        assert cashflow.reimbursementPoint == venue_ok

    @auto_override_features
    def test_no_cashflow_if_total_is_zero(self):
        venue = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(venue=venue)
        _pricing_total_is_zero_1 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue,
            amount=-1000,
        )
        _pricing_total_is_zero_2 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue,
            amount=1000,
        )
        _pricing_free_offer = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue,
            amount=0,
        )
        cutoff = datetime.datetime.utcnow()
        api.generate_cashflows(cutoff)
        assert models.Cashflow.query.count() == 0

    @auto_override_features
    def test_assert_num_queries(self):
        if self.use_reimbursement_point:
            venue1 = offerers_factories.VenueFactory(reimbursement_point="self")
            factories.BankInformationFactory(venue=venue1)
            venue2 = offerers_factories.VenueFactory(reimbursement_point="self")
            factories.BankInformationFactory(venue=venue2)
            factories.PricingFactory(
                status=models.PricingStatus.VALIDATED,
                booking__stock__offer__venue=venue1,
            )
            factories.PricingFactory(
                status=models.PricingStatus.VALIDATED,
                booking__stock__offer__venue=venue1,
            )
            factories.PricingFactory(
                status=models.PricingStatus.VALIDATED,
                booking__stock__offer__venue=venue2,
            )
        else:
            business_unit1 = factories.BusinessUnitFactory(siret="01234567890000")
            factories.PricingFactory(status=models.PricingStatus.VALIDATED, businessUnit=business_unit1)
            factories.PricingFactory(status=models.PricingStatus.VALIDATED, businessUnit=business_unit1)
            factories.PricingFactory(status=models.PricingStatus.VALIDATED)

        cutoff = datetime.datetime.utcnow()

        n_queries = 0
        n_queries += 1  # compute next CashflowBatch.label
        n_queries += 1  # insert CashflowBatch
        n_queries += 1  # commit
        n_queries += 1  # select CashflowBatch again after commit
        n_queries += 1  # select USE_REIMBURSEMENT_POINT_... feature flag
        n_queries += 1  # select business unit and bank account ids to process
        n_queries += 2 * sum(  # 2 business units
            (
                1,  # compute sum of pricings
                1,  # insert Cashflow
                1,  # select pricings to...
                1,  # ... insert CashflowPricing
                1,  # update Pricing.status
                1,  # commit
            )
        )
        with assert_num_queries(n_queries):
            api.generate_cashflows(cutoff)

        assert models.Cashflow.query.count() == 2


class LegacyGenerateCashflowsTest(GenerateCashflowsTest):
    use_reimbursement_point = False

    @auto_override_features
    def test_basics(self):
        now = datetime.datetime.utcnow()
        business_unit1 = factories.BusinessUnitFactory(siret="85331845900023")
        pricing11 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            businessUnit=business_unit1,
            amount=-1000,
        )
        pricing12 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            businessUnit=business_unit1,
            amount=-1000,
        )
        collective_pricing13 = factories.CollectivePricingFactory(
            status=models.PricingStatus.VALIDATED,
            businessUnit=business_unit1,
            amount=-500,
            collectiveBooking__collectiveStock__beginningDatetime=now - datetime.timedelta(days=1),
        )
        pricing2 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__beginningDatetime=now - datetime.timedelta(days=1),
            amount=-3000,
        )
        pricing_future_event = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__beginningDatetime=now + datetime.timedelta(days=1),
        )
        collective_pricing_future_event = factories.CollectivePricingFactory(
            status=models.PricingStatus.VALIDATED,
            collectiveBooking__collectiveStock__beginningDatetime=now + datetime.timedelta(days=1),
        )
        pricing_no_bank_account = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue__businessUnit__bankAccount=None,
        )
        pricing_pending = factories.PricingFactory(status=models.PricingStatus.PENDING)
        cutoff = datetime.datetime.utcnow()
        pricing_after_cutoff = factories.PricingFactory(status=models.PricingStatus.VALIDATED)

        batch_id = api.generate_cashflows(cutoff)

        batch = models.CashflowBatch.query.one()
        assert batch.id == batch_id
        assert batch.cutoff == cutoff
        assert pricing11.status == models.PricingStatus.PROCESSED
        assert pricing12.status == models.PricingStatus.PROCESSED
        assert collective_pricing13.status == models.PricingStatus.PROCESSED
        assert pricing2.status == models.PricingStatus.PROCESSED
        assert models.Cashflow.query.count() == 2
        assert len(pricing11.cashflows) == 1
        assert len(pricing12.cashflows) == 1
        assert len(collective_pricing13.cashflows) == 1
        assert pricing11.cashflows == pricing12.cashflows == collective_pricing13.cashflows
        assert len(pricing2.cashflows) == 1
        assert pricing11.cashflows[0].amount == -2500
        assert pricing11.cashflows[0].bankAccount == business_unit1.bankAccount
        assert pricing2.cashflows[0].amount == -3000

        assert not pricing_future_event.cashflows
        assert not collective_pricing_future_event.cashflows
        assert not pricing_no_bank_account.cashflows
        assert not pricing_pending.cashflows
        assert not pricing_after_cutoff.cashflows

    @auto_override_features
    def test_no_cashflow_if_total_is_zero(self):
        venue = offerers_factories.VenueFactory()
        business_unit = venue.businessUnit
        _pricing_total_is_zero_1 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue,
            businessUnit=business_unit,
            amount=-1000,
        )
        _pricing_total_is_zero_2 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue,
            businessUnit=business_unit,
            amount=1000,
        )
        _pricing_free_offer = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__offer__venue=venue,
            businessUnit=business_unit,
            amount=0,
        )
        cutoff = datetime.datetime.utcnow()
        api.generate_cashflows(cutoff)
        assert models.Cashflow.query.count() == 0

    def test_no_cashflow_if_no_accepted_bank_information(self):
        business_unit1 = factories.BusinessUnitFactory(bankAccount__status=models.BankInformationStatus.DRAFT)
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            businessUnit=business_unit1,
            amount=-1000,
        )
        business_unit2 = factories.BusinessUnitFactory(bankAccount=None)
        factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            businessUnit=business_unit2,
            amount=-2000,
        )

        cutoff = datetime.datetime.utcnow()
        api.generate_cashflows(cutoff)

        assert models.Cashflow.query.count() == 0

    @auto_override_features
    def test_create_cashflow_for_collective_bookings(self):
        now = datetime.datetime.utcnow()
        business_unit1 = factories.BusinessUnitFactory(siret="85331845900023")
        business_unit2 = factories.BusinessUnitFactory(siret="11223344555667")
        pricing = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            businessUnit=business_unit1,
            amount=-1000,
        )
        pricing_collective_booking = factories.CollectivePricingFactory(
            status=models.PricingStatus.VALIDATED,
            businessUnit=business_unit2,
            amount=-1000,
            collectiveBooking__collectiveStock__beginningDatetime=now - datetime.timedelta(days=1),
        )
        pricing_collective_booking_future_event = factories.CollectivePricingFactory(
            status=models.PricingStatus.VALIDATED,
            collectiveBooking__collectiveStock__beginningDatetime=now + datetime.timedelta(days=1),
        )
        cutoff = datetime.datetime.utcnow()

        batch_id = api.generate_cashflows(cutoff)

        batch = models.CashflowBatch.query.one()

        assert batch.id == batch_id
        assert batch.cutoff == cutoff
        assert pricing.status == models.PricingStatus.PROCESSED
        assert pricing_collective_booking.status == models.PricingStatus.PROCESSED
        assert pricing_collective_booking_future_event.status == models.PricingStatus.VALIDATED
        assert models.Cashflow.query.count() == 2
        assert len(pricing.cashflows) == 1
        assert len(pricing_collective_booking.cashflows) == 1
        assert pricing.cashflows[0].amount == -1000
        assert pricing.cashflows[0].bankAccount == business_unit1.bankAccount
        assert pricing_collective_booking.cashflows[0].amount == -1000
        assert pricing_collective_booking.cashflows[0].bankAccount == business_unit2.bankAccount

        assert not pricing_collective_booking_future_event.cashflows


@clean_temporary_files
@mock.patch("pcapi.connectors.googledrive.TestingBackend.create_file")
def test_generate_payment_files(mocked_gdrive_create_file):
    # The contents of generated files is unit-tested in other test
    # functions below.
    factories.PricingFactory(status=models.PricingStatus.VALIDATED)
    cutoff = datetime.datetime.utcnow()
    batch_id = api.generate_cashflows(cutoff)

    api.generate_payment_files(batch_id)

    cashflow = models.Cashflow.query.one()
    assert cashflow.status == models.CashflowStatus.UNDER_REVIEW
    assert len(cashflow.logs) == 1
    assert cashflow.logs[0].statusBefore == models.CashflowStatus.PENDING
    assert cashflow.logs[0].statusAfter == models.CashflowStatus.UNDER_REVIEW
    gdrive_file_names = {call.args[1] for call in mocked_gdrive_create_file.call_args_list}
    assert gdrive_file_names == {
        "business_units.csv",
        "payment_details.csv.zip",
        "soldes_des_utilisateurs.csv.zip",
    }


@clean_temporary_files
def test_generate_reimbursement_points_file():
    point1 = offerers_factories.VenueFactory(
        name='Name1\n "with double quotes"   ',
        siret='siret 1 "t"',
    )
    factories.BankInformationFactory(venue=point1, iban="some-iban", bic="some-bic")
    offerers_factories.VenueReimbursementPointLinkFactory(reimbursementPoint=point1)

    n_queries = 1  # select business unit data
    with assert_num_queries(n_queries):
        path = api._generate_reimbursement_points_file()

    with path.open(encoding="utf-8") as fp:
        reader = csv.DictReader(fp, quoting=csv.QUOTE_NONNUMERIC)
        rows = list(reader)
    assert len(rows) == 1
    assert rows[0] == {
        "Identifiant du point de remboursement": human_ids.humanize(point1.id),
        "SIRET": "siret 1 t",
        "Raison sociale du point de remboursement": "Name1 with double quotes",
        "IBAN": "some-iban",
        "BIC": "some-bic",
    }


@clean_temporary_files
def test_generate_business_units_file():
    venue1 = offerers_factories.VenueFactory(
        name='Venue 1 only name "doublequote" \n',
        publicName=None,
        siret='siret 1 "t"',
        businessUnit__name=' Business unit 1 "doublequote"\n',
        businessUnit__bankAccount__bic='bic 1 "t"\n',
        businessUnit__bankAccount__iban='iban 1 "t"\n',
    )
    business_unit1 = venue1.businessUnit
    offerers_factories.VenueFactory(businessUnit=business_unit1)
    venue2 = offerers_factories.VenueFactory(
        name="dummy, we should use publicName instead",
        siret="siret 2\n",
        publicName="Venue 2 public name\n",
        businessUnit__name="Business unit 2\n",
        businessUnit__bankAccount__bic="bic 2\n",
        businessUnit__bankAccount__iban="iban 2\n",
    )

    n_queries = 1  # select business unit data
    with assert_num_queries(n_queries):
        path = api._generate_business_units_file()

    with path.open(encoding="utf-8") as fp:
        reader = csv.DictReader(fp, quoting=csv.QUOTE_NONNUMERIC)
        rows = list(reader)
    assert len(rows) == 2
    assert rows[0] == {
        "Identifiant de la BU": human_ids.humanize(venue1.id),
        "SIRET": "siret 1 t",
        "Raison sociale de la BU": "Business unit 1 doublequote",
        "Libellé de la BU": "Venue 1 only name doublequote",
        "IBAN": "iban 1 t",
        "BIC": "bic 1 t",
    }
    assert rows[1] == {
        "Identifiant de la BU": human_ids.humanize(venue2.id),
        "SIRET": "siret 2",
        "Raison sociale de la BU": "Business unit 2",
        "Libellé de la BU": "Venue 2 public name",
        "IBAN": "iban 2",
        "BIC": "bic 2",
    }


@clean_temporary_files
@override_features(USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS=True)
def test_generate_payments_file():
    used_date = datetime.datetime(2020, 1, 2)
    # This pricing belong to a business unit whose venue is the same
    # as the venue of the offer.
    venue1 = offerers_factories.VenueFactory(
        name='Le Petit Rintintin "test"\n',
        siret='123456 "test"\n',
        pricing_point="self",
        reimbursement_point="self",
    )
    factories.BankInformationFactory(venue=venue1)
    factories.PricingFactory(
        amount=-1000,  # rate = 100 %
        booking__amount=10,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire formidable",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue1,
    )
    # A free booking that should not appear in the CSV file.
    factories.PricingFactory(
        amount=0,
        booking__amount=0,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire gratuite",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue1,
    )
    # These other pricings belong to a business unit whose venue is
    # NOT the venue of the offers.
    reimbursement_point_2 = offerers_factories.VenueFactory(
        siret="22222222233333",
        name="Point de remboursement du Gigantesque Cubitus\n",
    )
    factories.BankInformationFactory(venue=reimbursement_point_2)
    offer_venue2 = offerers_factories.VenueFactory(
        name="Le Gigantesque Cubitus\n",
        siret="99999999999999",
        pricing_point="self",
        reimbursement_point=reimbursement_point_2,
    )
    # the 2 pricings below should be merged together as they share the same BU and same deposit type
    factories.PricingFactory(
        amount=-900,  # rate = 75 %
        booking__amount=12,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=offer_venue2,
    )
    factories.PricingFactory(
        amount=-600,  # rate = 50 %
        booking__amount=12,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=offer_venue2,
        standardRule="",
        customRule=payments_factories.CustomReimbursementRuleFactory(amount=6),
    )
    # pricing for an underage individual booking
    underage_user = users_factories.UnderageBeneficiaryFactory()
    factories.PricingFactory(
        amount=-600,  # rate = 50 %
        booking__amount=12,
        booking__individualBooking__user=underage_user,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=offer_venue2,
        standardRule="",
        customRule=payments_factories.CustomReimbursementRuleFactory(amount=6),
    )
    # pricing for educational booking
    # check that the right deposit is used for csv
    year1 = EducationalYearFactory()
    year2 = EducationalYearFactory()
    year3 = EducationalYearFactory()
    educational_institution = EducationalInstitutionFactory()
    EducationalDepositFactory(
        educationalInstitution=educational_institution, educationalYear=year1, ministry=Ministry.AGRICULTURE.name
    )
    deposit2 = EducationalDepositFactory(
        educationalInstitution=educational_institution,
        educationalYear=year2,
        ministry=Ministry.EDUCATION_NATIONALE.name,
    )
    EducationalDepositFactory(
        educationalInstitution=educational_institution, educationalYear=year3, ministry=Ministry.ARMEES.name
    )
    # the 2 following pricing should be merged together in the csv file
    factories.CollectivePricingFactory(
        amount=-300,  # rate = 100 %
        collectiveBooking__collectiveStock__price=3,
        collectiveBooking__dateUsed=used_date,
        collectiveBooking__collectiveStock__beginningDatetime=used_date,
        collectiveBooking__collectiveStock__collectiveOffer__name="Une histoire plutôt bien",
        collectiveBooking__collectiveStock__collectiveOffer__subcategoryId=subcategories.CINE_PLEIN_AIR.id,
        collectiveBooking__collectiveStock__collectiveOffer__venue=offer_venue2,
        collectiveBooking__educationalInstitution=deposit2.educationalInstitution,
        collectiveBooking__educationalYear=deposit2.educationalYear,
    )
    factories.CollectivePricingFactory(
        amount=-700,  # rate = 100 %
        collectiveBooking__collectiveStock__price=7,
        collectiveBooking__dateUsed=used_date,
        collectiveBooking__collectiveStock__beginningDatetime=used_date,
        collectiveBooking__collectiveStock__collectiveOffer__name="Une histoire plutôt bien 2",
        collectiveBooking__collectiveStock__collectiveOffer__subcategoryId=subcategories.CINE_PLEIN_AIR.id,
        collectiveBooking__collectiveStock__collectiveOffer__venue=offer_venue2,
        collectiveBooking__educationalInstitution=deposit2.educationalInstitution,
        collectiveBooking__educationalYear=deposit2.educationalYear,
    )

    cutoff = datetime.datetime.utcnow()
    batch_id = api.generate_cashflows(cutoff)

    n_queries = 2  # select pricings for bookings + collective bookings
    with assert_num_queries(n_queries):
        path = api._generate_payments_file(batch_id)

    with zipfile.ZipFile(path) as zfile:
        with zfile.open("payment_details.csv") as csv_bytefile:
            csv_textfile = io.TextIOWrapper(csv_bytefile)
            reader = csv.DictReader(csv_textfile, quoting=csv.QUOTE_NONNUMERIC)
            rows = list(reader)

    assert len(rows) == 4
    assert rows[0] == {
        "Identifiant du point de remboursement": human_ids.humanize(venue1.id),
        "SIRET du point de remboursement": "123456 test",
        "Libellé du point de remboursement": "Le Petit Rintintin test",
        "Type de réservation": "PC",
        "Ministère": "",
        "Prix de la réservation": 10,
        "Montant remboursé à l'offreur": 10,
    }
    assert rows[1] == {
        "Identifiant du point de remboursement": human_ids.humanize(reimbursement_point_2.id),
        "SIRET du point de remboursement": "22222222233333",
        "Libellé du point de remboursement": "Point de remboursement du Gigantesque Cubitus",
        "Type de réservation": "EACI",
        "Ministère": "",
        "Prix de la réservation": 12,
        "Montant remboursé à l'offreur": 6,
    }
    assert rows[2] == {
        "Identifiant du point de remboursement": human_ids.humanize(reimbursement_point_2.id),
        "SIRET du point de remboursement": "22222222233333",
        "Libellé du point de remboursement": "Point de remboursement du Gigantesque Cubitus",
        "Type de réservation": "PC",
        "Ministère": "",
        "Prix de la réservation": 24,
        "Montant remboursé à l'offreur": 15,
    }
    assert rows[3] == {
        "Identifiant du point de remboursement": human_ids.humanize(reimbursement_point_2.id),
        "SIRET du point de remboursement": "22222222233333",
        "Libellé du point de remboursement": "Point de remboursement du Gigantesque Cubitus",
        "Type de réservation": "EACC",
        "Ministère": Ministry.EDUCATION_NATIONALE.name,
        "Prix de la réservation": 10,
        "Montant remboursé à l'offreur": 10,
    }


@clean_temporary_files
@override_features(USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS=False)
def test_generate_payments_file_legacy_with_business_units():
    used_date = datetime.datetime(2020, 1, 2)
    # This pricing belong to a business unit whose venue is the same
    # as the venue of the offer.
    venue1 = offerers_factories.VenueFactory(
        name='Le Petit Rintintin "test"\n',
        siret='123456 "test"\n',
    )
    factories.PricingFactory(
        amount=-1000,  # rate = 100 %
        booking__amount=10,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire formidable",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue1,
    )
    # A free booking that should not appear in the CSV file.
    factories.PricingFactory(
        amount=0,
        booking__amount=0,
        booking__dateUsed=used_date,
        booking__stock__offer__name='Une histoire "gratuite"\n',
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue1,
    )
    # These other pricings belong to a business unit whose venue is
    # NOT the venue of the offers.
    business_unit_venue2 = offerers_factories.VenueFactory(
        siret="22222222233333",
        name="BU du Gigantesque Cubitus\n",
    )
    business_unit2 = business_unit_venue2.businessUnit
    offer_venue2 = offerers_factories.VenueFactory(
        name="Le Gigantesque Cubitus\n",
        siret="99999999999999",
        businessUnit=business_unit2,
    )
    # the 2 pricings below should be merged together as they share the same BU and same deposit type
    factories.PricingFactory(
        amount=-900,  # rate = 75 %
        booking__amount=12,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=offer_venue2,
    )
    factories.PricingFactory(
        amount=-600,  # rate = 50 %
        booking__amount=12,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=offer_venue2,
        standardRule="",
        customRule=payments_factories.CustomReimbursementRuleFactory(amount=6),
    )
    # pricing for an underage individual booking
    underage_user = users_factories.UnderageBeneficiaryFactory()
    factories.PricingFactory(
        amount=-600,  # rate = 50 %
        booking__amount=12,
        booking__individualBooking__user=underage_user,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=offer_venue2,
        standardRule="",
        customRule=payments_factories.CustomReimbursementRuleFactory(amount=6),
    )
    # pricing for educational booking
    # check that the right deposit is used for csv
    year1 = EducationalYearFactory()
    year2 = EducationalYearFactory()
    year3 = EducationalYearFactory()
    educational_institution = EducationalInstitutionFactory()
    EducationalDepositFactory(
        educationalInstitution=educational_institution, educationalYear=year1, ministry=Ministry.AGRICULTURE.name
    )
    deposit2 = EducationalDepositFactory(
        educationalInstitution=educational_institution,
        educationalYear=year2,
        ministry=Ministry.EDUCATION_NATIONALE.name,
    )
    EducationalDepositFactory(
        educationalInstitution=educational_institution, educationalYear=year3, ministry=Ministry.ARMEES.name
    )
    # A pricing that belongs to a business unit whose SIRET is not a
    # SIRET of any venue.
    pricing6 = factories.PricingFactory(
        amount=-1000,  # rate = 100 %
        booking__dateUsed=used_date,
        booking__stock__offer__venue__businessUnit__siret="orphan siret",
    )
    # the 2 following pricing should be merged together in the csv file
    factories.CollectivePricingFactory(
        amount=-300,  # rate = 100 %
        collectiveBooking__collectiveStock__price=3,
        collectiveBooking__dateUsed=used_date,
        collectiveBooking__collectiveStock__beginningDatetime=used_date,
        collectiveBooking__collectiveStock__collectiveOffer__name="Une histoire plutôt bien",
        collectiveBooking__collectiveStock__collectiveOffer__subcategoryId=subcategories.CINE_PLEIN_AIR.id,
        collectiveBooking__collectiveStock__collectiveOffer__venue=offer_venue2,
        collectiveBooking__educationalInstitution=deposit2.educationalInstitution,
        collectiveBooking__educationalYear=deposit2.educationalYear,
    )
    factories.CollectivePricingFactory(
        amount=-700,  # rate = 100 %
        collectiveBooking__collectiveStock__price=7,
        collectiveBooking__dateUsed=used_date,
        collectiveBooking__collectiveStock__beginningDatetime=used_date,
        collectiveBooking__collectiveStock__collectiveOffer__name="Une histoire plutôt bien 2",
        collectiveBooking__collectiveStock__collectiveOffer__subcategoryId=subcategories.CINE_PLEIN_AIR.id,
        collectiveBooking__collectiveStock__collectiveOffer__venue=offer_venue2,
        collectiveBooking__educationalInstitution=deposit2.educationalInstitution,
        collectiveBooking__educationalYear=deposit2.educationalYear,
    )

    cutoff = datetime.datetime.utcnow()
    batch_id = api.generate_cashflows(cutoff)

    n_queries = 2  # select pricings for bookings + collective bookings
    with assert_num_queries(n_queries):
        path = api._generate_payments_file(batch_id)

    with zipfile.ZipFile(path) as zfile:
        with zfile.open("payment_details.csv") as csv_bytefile:
            csv_textfile = io.TextIOWrapper(csv_bytefile)
            reader = csv.DictReader(csv_textfile, quoting=csv.QUOTE_NONNUMERIC)
            rows = list(reader)

    assert len(rows) == 5
    assert rows[0] == {
        "Identifiant de la BU": human_ids.humanize(venue1.id),
        "SIRET de la BU": "123456 test",
        "Libellé de la BU": "Le Petit Rintintin test",
        "Type de réservation": "PC",
        "Ministère": "",
        "Prix de la réservation": 10,
        "Montant remboursé à l'offreur": 10,
    }
    assert rows[1] == {
        "Identifiant de la BU": human_ids.humanize(business_unit_venue2.id),
        "SIRET de la BU": "22222222233333",
        "Libellé de la BU": "BU du Gigantesque Cubitus",
        "Type de réservation": "EACI",
        "Ministère": "",
        "Prix de la réservation": 12,
        "Montant remboursé à l'offreur": 6,
    }
    assert rows[2] == {
        "Identifiant de la BU": human_ids.humanize(business_unit_venue2.id),
        "SIRET de la BU": "22222222233333",
        "Libellé de la BU": "BU du Gigantesque Cubitus",
        "Type de réservation": "PC",
        "Ministère": "",
        "Prix de la réservation": 24,
        "Montant remboursé à l'offreur": 15,
    }
    assert rows[3] == {
        # Some fields are empty since there are no corresponding venue.
        "Identifiant de la BU": "",
        "SIRET de la BU": "orphan siret",
        "Libellé de la BU": "",
        "Type de réservation": "PC",
        "Ministère": "",
        "Prix de la réservation": pricing6.booking.total_amount,
        "Montant remboursé à l'offreur": 10,
    }
    assert rows[4] == {
        "Identifiant de la BU": human_ids.humanize(business_unit_venue2.id),
        "SIRET de la BU": "22222222233333",
        "Libellé de la BU": "BU du Gigantesque Cubitus",
        "Type de réservation": "EACC",
        "Ministère": Ministry.EDUCATION_NATIONALE.name,
        "Prix de la réservation": 10,
        "Montant remboursé à l'offreur": 10,
    }


@clean_temporary_files
def test_generate_wallets_file():
    user1 = users_factories.BeneficiaryGrant18Factory(deposit__version=1)
    bookings_factories.IndividualBookingFactory(individualBooking__user=user1, amount=10)
    bookings_factories.UsedIndividualBookingFactory(individualBooking__user=user1, amount=20)
    bookings_factories.CancelledIndividualBookingFactory(individualBooking__user=user1, amount=30)
    user2 = users_factories.BeneficiaryGrant18Factory(deposit__version=2)
    bookings_factories.UsedIndividualBookingFactory(individualBooking__user=user2, amount=10)
    users_factories.ProFactory()  # no wallet for this one

    path = api._generate_wallets_file()

    with zipfile.ZipFile(path) as zfile:
        with zfile.open("soldes_des_utilisateurs.csv") as csv_bytefile:
            csv_textfile = io.TextIOWrapper(csv_bytefile)
            reader = csv.DictReader(csv_textfile, quoting=csv.QUOTE_NONNUMERIC)
            rows = list(reader)
    assert len(rows) == 2
    assert rows[0] == {
        "ID de l'utilisateur": user1.id,
        "Solde théorique": 500 - 10 - 20,
        "Solde réel": 500 - 20,
    }
    assert rows[1] == {
        "ID de l'utilisateur": user2.id,
        "Solde théorique": 300 - 10,
        "Solde réel": 300 - 10,
    }


@clean_temporary_files
@override_features(USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS=True)
def test_generate_invoice_file():
    first_siret = "12345678900"
    reimbursement_point1 = offerers_factories.VenueFactory(siret=first_siret)
    bank_info1 = factories.BankInformationFactory(venue=reimbursement_point1)
    offerer1 = reimbursement_point1.managingOfferer
    pricing_point1 = offerers_factories.VenueFactory(managingOfferer=offerer1)
    offerers_factories.VenueFactory(
        managingOfferer=offerer1,
        pricing_point=pricing_point1,
        reimbursement_point=reimbursement_point1,
    )
    pricing1 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        pricingPoint=pricing_point1,
        amount=-1000,
    )
    pline11 = factories.PricingLineFactory(pricing=pricing1)
    pline12 = factories.PricingLineFactory(
        pricing=pricing1,
        amount=100,
        category=models.PricingLineCategory.OFFERER_CONTRIBUTION,
    )
    cashflow1 = factories.CashflowFactory(
        bankAccount=bank_info1,
        reimbursementPoint=reimbursement_point1,
        pricings=[pricing1],
        status=models.CashflowStatus.ACCEPTED,
    )
    invoice1 = factories.InvoiceFactory(
        reimbursementPoint=reimbursement_point1,
        cashflows=[cashflow1],
    )

    # The file should contains only cashflow from the current batch of invoice generation.
    # This second invoice should not appear.
    second_siret = "12345673900"
    reimbursement_point2 = offerers_factories.VenueFactory(siret=second_siret)
    bank_info2 = factories.BankInformationFactory(venue=reimbursement_point2)
    offerer2 = reimbursement_point2.managingOfferer
    pricing_point2 = offerers_factories.VenueFactory(managingOfferer=offerer2)
    offerers_factories.VenueFactory(
        managingOfferer=offerer2,
        pricing_point=pricing_point2,
        reimbursement_point=reimbursement_point2,
    )
    pline2 = factories.PricingLineFactory()
    pricing2 = pline2.pricing
    cashflow2 = factories.CashflowFactory(
        bankAccount=bank_info2,
        reimbursementPoint=reimbursement_point2,
        pricings=[pricing2],
        status=models.CashflowStatus.ACCEPTED,
    )
    factories.InvoiceFactory(
        reimbursementPoint=reimbursement_point2,
        cashflows=[cashflow2],
        reference="not displayed because on a different date",
        date=datetime.datetime(2022, 1, 1),
    )

    path = api.generate_invoice_file(datetime.date.today(), use_reimbursement_point=True)
    with zipfile.ZipFile(path) as zfile:
        with zfile.open("invoices.csv") as csv_bytefile:
            csv_textfile = io.TextIOWrapper(csv_bytefile)
            reader = csv.DictReader(csv_textfile, quoting=csv.QUOTE_NONNUMERIC)
            rows = list(reader)
    assert len(rows) == 2
    assert rows[0] == {
        "Identifiant du point de remboursement": human_ids.humanize(reimbursement_point1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Identifiant valorisation": pricing1.id,
        "Identifiant ticket de facturation": pline11.id,
        "type de ticket de facturation": pline11.category.value,
        "montant du ticket de facturation": abs(pline11.amount),
    }
    assert rows[1] == {
        "Identifiant du point de remboursement": human_ids.humanize(reimbursement_point1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice1.reference,
        "Identifiant valorisation": pricing1.id,
        "Identifiant ticket de facturation": pline12.id,
        "type de ticket de facturation": pline12.category.value,
        "montant du ticket de facturation": abs(pline12.amount),
    }


@clean_temporary_files
def test_generate_invoice_file_with_legacy_business_unit():
    first_siret = "12345678900"
    business_unit1 = factories.BusinessUnitFactory(siret=first_siret)
    venue1 = offerers_factories.VenueFactory(businessUnit=business_unit1, siret=first_siret)

    pc_line1 = factories.PricingLineFactory()
    pc_line2 = factories.PricingLineFactory(amount=150000, category=models.PricingLineCategory.OFFERER_CONTRIBUTION)
    pricing = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED, businessUnit=business_unit1, amount=-1000, lines=[pc_line1, pc_line2]
    )
    pricing1 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED,
        businessUnit=business_unit1,
        amount=-1000,
    )
    cashFlow = factories.CashflowFactory(
        bankAccount=business_unit1.bankAccount,
        pricings=[pricing, pricing1],
        status=models.CashflowStatus.ACCEPTED,
        batchId=1,
        amount=-1000,
    )
    invoice = factories.InvoiceFactory(businessUnit=business_unit1, cashflows=[cashFlow], reference="displayed Invoice")

    # The file should contains only cashflow from the current batch of invoice generation.
    # This second invoice should not appear.
    second_siret = "12345673900"
    business_unit2 = factories.BusinessUnitFactory(siret=second_siret)
    offerers_factories.VenueFactory(businessUnit=business_unit2, siret=second_siret)

    pc_line3 = factories.PricingLineFactory()
    pricing2 = factories.PricingFactory(
        status=models.PricingStatus.VALIDATED, businessUnit=business_unit2, amount=-1000, lines=[pc_line3]
    )
    cashFlow2 = factories.CashflowFactory(
        bankAccount=business_unit2.bankAccount,
        pricings=[pricing2],
        status=models.CashflowStatus.ACCEPTED,
        batchId=1,
        amount=-1000,
    )
    factories.InvoiceFactory(
        businessUnit=business_unit2,
        cashflows=[cashFlow2],
        reference="not displayed",
        date=datetime.datetime(2022, 1, 1),
    )

    path = api.generate_invoice_file(datetime.date.today(), use_reimbursement_point=False)
    with zipfile.ZipFile(path) as zfile:
        with zfile.open("invoices.csv") as csv_bytefile:
            csv_textfile = io.TextIOWrapper(csv_bytefile)
            reader = csv.DictReader(csv_textfile, quoting=csv.QUOTE_NONNUMERIC)
            rows = list(reader)
    assert len(rows) == 2
    assert rows[0] == {
        "Identifiant de la BU": human_ids.humanize(venue1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice.reference,
        "Identifiant valorisation": pricing.id,
        "Identifiant ticket de facturation": pc_line1.id,
        "type de ticket de facturation": pc_line1.category.value,
        "montant du ticket de facturation": abs(pc_line1.amount),
    }
    assert rows[1] == {
        "Identifiant de la BU": human_ids.humanize(venue1.id),
        "Date du justificatif": datetime.date.today().isoformat(),
        "Référence du justificatif": invoice.reference,
        "Identifiant valorisation": pricing.id,
        "Identifiant ticket de facturation": pc_line2.id,
        "type de ticket de facturation": pc_line2.category.value,
        "montant du ticket de facturation": abs(pc_line2.amount),
    }


class EditBusinessUnitTest:
    def test_edit_siret(self):
        venue = offerers_factories.VenueFactory(
            businessUnit__siret=None,
            managingOfferer__siren="123456789",
            siret="12345678901234",
        )
        business_unit = venue.businessUnit

        api.edit_business_unit(business_unit, siret="12345678901234")

        business_unit = models.BusinessUnit.query.one()
        assert business_unit.siret == "12345678901234"
        assert business_unit.name == venue.publicName

    def test_cannot_edit_siret_if_one_is_already_set(self):
        venue = offerers_factories.VenueFactory(
            businessUnit__siret="12345678901234",
            managingOfferer__siren="123456789",
        )
        business_unit = venue.businessUnit

        with pytest.raises(ValueError):
            api.edit_business_unit(business_unit, siret="123456789")

    def test_cannot_edit_siret_if_already_used(self):
        venue = offerers_factories.VenueFactory(
            businessUnit__siret=None,
            managingOfferer__siren="123456789",
        )
        business_unit = venue.businessUnit
        existing = factories.BusinessUnitFactory(siret="12345678901234")

        with pytest.raises(exceptions.InvalidSiret):
            api.edit_business_unit(business_unit, siret=existing.siret)


# FIXME (dbaty, 2022-07-19): Once tests do not use business units
# anymore, this function could be turned back into a pytest fixture.
# @pytest.fixture(name="invoice_data")
def invoice_test_data(use_reimbursement_point):
    if use_reimbursement_point:
        venue_kwargs = {
            "businessUnit": None,
            "pricing_point": "self",
            "reimbursement_point": "self",
        }
    else:
        venue_kwargs = {
            "businessUnit__bankAccount__iban": "FR2710010000000000000000064",
        }
    venue = offerers_factories.VenueFactory(
        name="Coiffeur justificaTIF",
        siret="85331845900023",
        bookingEmail="pro@example.com",
        **venue_kwargs,
    )
    if use_reimbursement_point:
        factories.BankInformationFactory(venue=venue, iban="FR2710010000000000000000064")

    business_unit = venue.businessUnit
    reimbursement_point = venue
    thing_offer1 = offers_factories.ThingOfferFactory(venue=venue)
    thing_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    book_offer1 = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    book_offer2 = offers_factories.OfferFactory(venue=venue, subcategoryId=subcategories.LIVRE_PAPIER.id)
    digital_offer1 = offers_factories.DigitalOfferFactory(venue=venue)
    digital_offer2 = offers_factories.DigitalOfferFactory(venue=venue)
    custom_rule_offer1 = offers_factories.ThingOfferFactory(venue=venue)
    payments_factories.CustomReimbursementRuleFactory(rate=0.94, offer=custom_rule_offer1)
    custom_rule_offer2 = offers_factories.ThingOfferFactory(venue=venue)
    payments_factories.CustomReimbursementRuleFactory(amount=22, offer=custom_rule_offer2)

    stocks = [
        offers_factories.StockFactory(offer=thing_offer1, price=30),
        offers_factories.StockFactory(offer=book_offer1, price=20),
        offers_factories.StockFactory(offer=thing_offer2, price=19_950),
        offers_factories.StockFactory(offer=thing_offer2, price=81.3),
        offers_factories.StockFactory(offer=book_offer2, price=40),
        offers_factories.StockFactory(offer=digital_offer1, price=27),
        offers_factories.StockFactory(offer=digital_offer2, price=31),
        offers_factories.StockFactory(offer=custom_rule_offer1, price=20),
        offers_factories.StockFactory(offer=custom_rule_offer2, price=23),
    ]

    return business_unit, reimbursement_point, stocks, venue


class GenerateInvoicesTest:
    use_pricing_point = True
    use_reimbursement_point = True
    stock_factory = individual_stock_factory

    # Mock slow functions that we are not interested in.
    @mock.patch("pcapi.core.finance.api._generate_invoice_html")
    @mock.patch("pcapi.core.finance.api._store_invoice_pdf")
    @auto_override_features
    def test_basics(self, _mocked1, _mocked2):
        booking1 = bookings_factories.UsedIndividualBookingFactory(stock=self.stock_factory())
        booking2 = bookings_factories.UsedIndividualBookingFactory(stock=self.stock_factory())
        booking3 = bookings_factories.UsedIndividualBookingFactory(stock=booking1.stock)
        booking4 = bookings_factories.UsedIndividualBookingFactory(stock=self.stock_factory())
        for booking in (booking1, booking2, booking3, booking4):
            factories.BankInformationFactory(venue=booking.venue)

        # Cashflows for booking1 and booking2 will be UNDER_REVIEW.
        api.price_booking(booking1, self.use_pricing_point)
        api.price_booking(booking2, self.use_pricing_point)
        api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())

        # Another cashflow for booking3 that has the same business
        # Unit as booking2.
        api.price_booking(booking3, self.use_pricing_point)
        api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())

        # Cashflow for booking4 will still be PENDING. No invoice
        # should be generated.
        api.price_booking(booking4, self.use_pricing_point)
        api.generate_cashflows(datetime.datetime.utcnow())

        api.generate_invoices()

        invoices = models.Invoice.query.all()
        assert len(invoices) == 2
        invoiced_bookings = {inv.cashflows[0].pricings[0].booking for inv in invoices}
        assert invoiced_bookings == {booking1, booking2}


class LegacyGenerateInvoicesTest(GenerateInvoicesTest):
    use_pricing_point = False
    use_reimbursement_point = False


class GenerateInvoiceTest:
    use_pricing_point = True
    use_reimbursement_point = True
    stock_factory = individual_stock_factory

    EXPECTED_NUM_QUERIES = (
        1  # select cashflows, pricings, pricing_lines, and custom_reimbursement_rules
        + 1  # select and lock ReferenceScheme
        + 1  # update ReferenceScheme
        + 1  # insert invoice
        + 1  # insert invoice lines
        + 1  # select cashflows
        + 1  # insert invoice_cashflows
        + 1  # update Cashflow.status
        + 1  # update Pricing.status
        + 1  # update Booking.status
        + 1  # FF is cached in all test due to generate_cashflows call
        + 1  # commit
    )

    @auto_override_features
    def test_reference_scheme_increments(self):
        venue = offerers_factories.VenueFactory(siret="85331845900023")
        business_unit = venue.businessUnit
        reimbursement_point = venue
        invoice1 = api._generate_invoice(
            business_unit_id=None if self.use_reimbursement_point else business_unit.id,
            reimbursement_point_id=reimbursement_point.id if self.use_reimbursement_point else None,
            cashflow_ids=[1, 2],
        )
        invoice2 = api._generate_invoice(
            business_unit_id=None if self.use_reimbursement_point else business_unit.id,
            reimbursement_point_id=reimbursement_point.id if self.use_reimbursement_point else None,
            cashflow_ids=[1, 2],
        )

        assert invoice1.reference == "F220000001"
        assert invoice2.reference == "F220000002"

    @auto_override_features
    def test_one_regular_rule_one_rate(self):
        if self.use_reimbursement_point:
            reimbursement_point = offerers_factories.VenueFactory()
            factories.BankInformationFactory(venue=reimbursement_point)
            venue = offerers_factories.VenueFactory(
                managingOfferer=reimbursement_point.managingOfferer,
                pricing_point="self",
                reimbursement_point=reimbursement_point,
                businessUnit=None,
            )
            reimbursement_point_id = reimbursement_point.id
            business_unit_id = venue.businessUnitId
        else:
            venue = offerers_factories.VenueFactory()
            business_unit_id = venue.businessUnit.id
            reimbursement_point_id = None

        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=20)
        booking1 = bookings_factories.UsedIndividualBookingFactory(stock=stock)
        booking2 = bookings_factories.UsedIndividualBookingFactory(stock=stock)
        api.price_booking(booking1, self.use_pricing_point)
        api.price_booking(booking2, self.use_pricing_point)
        api.generate_cashflows(datetime.datetime.utcnow())
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(
                business_unit_id=business_unit_id,
                reimbursement_point_id=reimbursement_point_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.reference == "F220000001"
        assert invoice.businessUnitId == venue.businessUnitId
        if self.use_reimbursement_point:
            assert invoice.reimbursementPoint == reimbursement_point
        assert invoice.amount == -40 * 100
        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème général", "position": 1}
        assert line.contributionAmount == 0
        assert line.reimbursedAmount == -40 * 100
        assert line.rate == 1
        assert line.label == "Montant remboursé"

    @auto_override_features
    def test_two_regular_rules_two_rates(self):
        if self.use_reimbursement_point:
            reimbursement_point = offerers_factories.VenueFactory()
            factories.BankInformationFactory(venue=reimbursement_point)
            venue = offerers_factories.VenueFactory(
                managingOfferer=reimbursement_point.managingOfferer,
                pricing_point="self",
                reimbursement_point=reimbursement_point,
                businessUnit=None,
            )
            reimbursement_point_id = reimbursement_point.id
            business_unit_id = venue.businessUnitId
        else:
            venue = offerers_factories.VenueFactory()
            business_unit_id = venue.businessUnit.id
            reimbursement_point_id = None

        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock1 = offers_factories.ThingStockFactory(offer=offer, price=19_850)
        stock2 = offers_factories.ThingStockFactory(offer=offer, price=160)
        user = create_rich_user()
        booking1 = bookings_factories.UsedIndividualBookingFactory(
            stock=stock1,
            individualBooking__user=user,
        )
        booking2 = bookings_factories.UsedIndividualBookingFactory(stock=stock2)
        api.price_booking(booking1, self.use_pricing_point)
        api.price_booking(booking2, self.use_pricing_point)
        api.generate_cashflows(datetime.datetime.utcnow())
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(
                business_unit_id=business_unit_id,
                reimbursement_point_id=reimbursement_point_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.reference == "F220000001"
        assert invoice.businessUnitId == business_unit_id
        if self.use_reimbursement_point:
            assert invoice.reimbursementPoint == reimbursement_point
        # 100% of 19_850*100 + 95% of 160*100 aka 152*100
        assert invoice.amount == -20_002 * 100
        assert len(invoice.lines) == 2
        invoice_lines = sorted(invoice.lines, key=lambda x: x.rate, reverse=True)

        line_rate_1 = invoice_lines[0]
        assert line_rate_1.group == {"label": "Barème général", "position": 1}
        assert line_rate_1.contributionAmount == 0
        assert line_rate_1.reimbursedAmount == -19_850 * 100
        assert line_rate_1.rate == 1
        assert line_rate_1.label == "Montant remboursé"
        line_rate_0_95 = invoice_lines[1]
        assert line_rate_0_95.group == {"label": "Barème général", "position": 1}
        assert line_rate_0_95.contributionAmount == 8 * 100
        assert line_rate_0_95.reimbursedAmount == -152 * 100
        assert line_rate_0_95.rate == Decimal("0.95")
        assert line_rate_0_95.label == "Montant remboursé"

    @auto_override_features
    def test_one_custom_rule(self):
        if self.use_reimbursement_point:
            reimbursement_point = offerers_factories.VenueFactory()
            factories.BankInformationFactory(venue=reimbursement_point)
            venue = offerers_factories.VenueFactory(
                managingOfferer=reimbursement_point.managingOfferer,
                pricing_point="self",
                reimbursement_point=reimbursement_point,
                businessUnit=None,
            )
            reimbursement_point_id = reimbursement_point.id
            business_unit_id = venue.businessUnitId
        else:
            venue = offerers_factories.VenueFactory()
            business_unit_id = venue.businessUnit.id
            reimbursement_point_id = None

        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=23)
        payments_factories.CustomReimbursementRuleFactory(amount=22, offer=offer)
        booking1 = bookings_factories.UsedIndividualBookingFactory(stock=stock)
        booking2 = bookings_factories.UsedIndividualBookingFactory(stock=stock)
        api.price_booking(booking1, self.use_pricing_point)
        api.price_booking(booking2, self.use_pricing_point)
        api.generate_cashflows(datetime.datetime.utcnow())
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(
                business_unit_id=business_unit_id,
                reimbursement_point_id=reimbursement_point_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.reference == "F220000001"
        assert invoice.businessUnitId == business_unit_id
        if self.use_reimbursement_point:
            assert invoice.reimbursementPoint == reimbursement_point
        assert invoice.amount == -4400
        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème dérogatoire", "position": 4}
        assert line.contributionAmount == 200
        assert line.reimbursedAmount == -4400
        assert line.rate == Decimal("0.9565")
        assert line.label == "Montant remboursé"

    @auto_override_features
    def test_many_rules_and_rates_two_cashflows(self):
        business_unit, reimbursement_point, stocks, _venue = invoice_test_data(self.use_reimbursement_point)
        bookings = []
        user = create_rich_user()
        for stock in stocks:
            booking = bookings_factories.UsedIndividualBookingFactory(
                stock=stock,
                user=user,
                individualBooking__user=user,
            )
            bookings.append(booking)
        for booking in bookings[:3]:
            api.price_booking(booking, self.use_pricing_point)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        for booking in bookings[3:]:
            api.price_booking(booking, self.use_pricing_point)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]
        business_unit_id = business_unit.id if business_unit else None
        reimbursement_point_id = reimbursement_point.id if reimbursement_point else None

        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(
                business_unit_id=business_unit_id,
                reimbursement_point_id=reimbursement_point_id,
                cashflow_ids=cashflow_ids,
            )

        assert len(invoice.cashflows) == 2
        assert invoice.reference == "F220000001"
        assert invoice.businessUnit == business_unit
        assert invoice.reimbursementPoint == reimbursement_point
        assert invoice.amount == -20_156_04
        # général 100%, général 95%, livre 100%, livre 95%, pas remboursé, custom 1, custom 2
        assert len(invoice.lines) == 7

        # sort by group position asc then rate desc, as displayed in the PDF
        invoice_lines = sorted(invoice.lines, key=lambda k: (k.group["position"], -k.rate))

        line0 = invoice_lines[0]
        assert line0.group == {"label": "Barème général", "position": 1}
        assert line0.contributionAmount == 0
        assert line0.reimbursedAmount == -19_980 * 100  # 19_950 + 30
        assert line0.rate == Decimal("1.0000")
        assert line0.label == "Montant remboursé"

        line1 = invoice_lines[1]
        assert line1.group == {"label": "Barème général", "position": 1}
        assert line1.contributionAmount == 406
        assert line1.reimbursedAmount == -7724
        assert line1.rate == Decimal("0.9500")
        assert line1.label == "Montant remboursé"

        line2 = invoice_lines[2]
        assert line2.group == {"label": "Barème livres", "position": 2}
        assert line2.contributionAmount == 0
        assert line2.reimbursedAmount == -20 * 100
        assert line2.rate == Decimal("1.0000")
        assert line2.label == "Montant remboursé"

        line3 = invoice_lines[3]
        assert line3.group == {"label": "Barème livres", "position": 2}
        assert line3.contributionAmount == 2 * 100
        assert line3.reimbursedAmount == -38 * 100
        assert line3.rate == Decimal("0.9500")
        assert line3.label == "Montant remboursé"

        line4 = invoice_lines[4]
        assert line4.group == {"label": "Barème non remboursé", "position": 3}
        assert line4.contributionAmount == 58 * 100
        assert line4.reimbursedAmount == 0
        assert line4.rate == Decimal("0.0000")
        assert line4.label == "Montant remboursé"

        line5 = invoice_lines[5]
        assert line5.group == {"label": "Barème dérogatoire", "position": 4}
        assert line5.contributionAmount == 100
        assert line5.reimbursedAmount == -22 * 100
        assert line5.rate == Decimal("0.9565")
        assert line5.label == "Montant remboursé"

        line6 = invoice_lines[6]
        assert line6.group == {"label": "Barème dérogatoire", "position": 4}
        assert line6.contributionAmount == 120
        assert line6.reimbursedAmount == -1880
        assert line6.rate == Decimal("0.9400")
        assert line6.label == "Montant remboursé"

    @auto_override_features
    def test_with_free_offer(self):
        if self.use_reimbursement_point:
            reimbursement_point = offerers_factories.VenueFactory()
            factories.BankInformationFactory(venue=reimbursement_point)
            venue = offerers_factories.VenueFactory(
                managingOfferer=reimbursement_point.managingOfferer,
                pricing_point="self",
                reimbursement_point=reimbursement_point,
                businessUnit=None,
            )
            reimbursement_point_id = reimbursement_point.id
            business_unit_id = venue.businessUnitId
        else:
            venue = offerers_factories.VenueFactory()
            business_unit_id = venue.businessUnit.id
            reimbursement_point_id = None

        # 2 offers that have a distinct reimbursement rate rule.
        offer1 = offers_factories.ThingOfferFactory(
            venue=venue,
            product__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        )
        stock1 = offers_factories.StockFactory(offer=offer1, price=20)
        booking1 = bookings_factories.UsedIndividualBookingFactory(stock=stock1)
        offer2 = offers_factories.ThingOfferFactory(
            venue=venue,
            product__subcategoryId=subcategories.TELECHARGEMENT_MUSIQUE.id,
        )
        stock2 = offers_factories.StockFactory(offer=offer2, price=0)
        booking2 = bookings_factories.UsedIndividualBookingFactory(stock=stock2)
        api.price_booking(booking1, self.use_pricing_point)
        api.price_booking(booking2, self.use_pricing_point)
        api.generate_cashflows(datetime.datetime.utcnow())
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]

        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(
                business_unit_id=business_unit_id,
                reimbursement_point_id=reimbursement_point_id,
                cashflow_ids=cashflow_ids,
            )

        assert invoice.reference == "F220000001"
        assert invoice.amount == -20 * 100
        assert len(invoice.lines) == 2
        line1 = invoice.lines[0]
        assert line1.group == {"label": "Barème général", "position": 1}
        assert line1.contributionAmount == 0
        assert line1.reimbursedAmount == -20 * 100
        assert line1.rate == 1
        assert line1.label == "Montant remboursé"
        line2 = invoice.lines[1]
        assert line2.group == {"label": "Barème non remboursé", "position": 3}
        assert line2.contributionAmount == 0
        assert line2.reimbursedAmount == 0
        assert line2.rate == 0
        assert line2.label == "Montant remboursé"

    @auto_override_features
    def test_update_statuses(self):
        stock = self.stock_factory()
        booking1 = bookings_factories.UsedBookingFactory(stock=stock)
        booking2 = bookings_factories.UsedBookingFactory(stock=stock)
        api.price_booking(booking1, self.use_pricing_point)
        api.price_booking(booking2, self.use_pricing_point)
        api.generate_cashflows(datetime.datetime.utcnow())
        cashflow_ids = {cf.id for cf in models.Cashflow.query.all()}
        booking2.status = bookings_models.BookingStatus.CANCELLED
        db.session.add(booking2)
        db.session.commit()

        api._generate_invoice(
            business_unit_id=booking1.venue.businessUnitId,
            reimbursement_point_id=booking1.venue.current_reimbursement_point_id,
            cashflow_ids=cashflow_ids,
        )

        get_statuses = lambda model: {s for s, in model.query.with_entities(getattr(model, "status"))}
        cashflow_statuses = get_statuses(models.Cashflow)
        assert cashflow_statuses == {models.CashflowStatus.ACCEPTED}
        pricing_statuses = get_statuses(models.Pricing)
        assert pricing_statuses == {models.PricingStatus.INVOICED}
        assert booking1.status == bookings_models.BookingStatus.REIMBURSED  # updated
        assert booking2.status == bookings_models.BookingStatus.CANCELLED  # not updated

    @auto_override_features
    def test_update_statuses_when_new_model_is_enabled(self):
        past = datetime.datetime.utcnow() - datetime.timedelta(days=1)
        booking1 = bookings_factories.UsedEducationalBookingFactory(
            stock=self.stock_factory(beginningDatetime=past),
        )
        collective_booking1 = UsedCollectiveBookingFactory(
            bookingId=booking1.id,
            collectiveStock__collectiveOffer__venue=booking1.venue,
            collectiveStock__beginningDatetime=past,
        )
        collective_booking2 = UsedCollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue=booking1.venue,
            collectiveStock__beginningDatetime=past,
        )
        api.price_booking(booking1, self.use_pricing_point)
        api.price_booking(collective_booking1, self.use_pricing_point)
        api.price_booking(collective_booking2, self.use_pricing_point)
        api.generate_cashflows(datetime.datetime.utcnow())
        cashflow_ids = {cf.id for cf in models.Cashflow.query.all()}

        api._generate_invoice(
            business_unit_id=booking1.venue.businessUnitId,
            reimbursement_point_id=booking1.venue.current_reimbursement_point_id,
            cashflow_ids=cashflow_ids,
        )

        get_statuses = lambda model: {s for s, in model.query.with_entities(getattr(model, "status"))}
        cashflow_statuses = get_statuses(models.Cashflow)
        assert cashflow_statuses == {models.CashflowStatus.ACCEPTED}
        pricing_statuses = get_statuses(models.Pricing)
        assert pricing_statuses == {models.PricingStatus.INVOICED}
        assert booking1.status == bookings_models.BookingStatus.REIMBURSED  # updated
        assert collective_booking1.status == CollectiveBookingStatus.REIMBURSED  # updated
        assert collective_booking2.status == CollectiveBookingStatus.REIMBURSED  # updated


class LegacyGenerateInvoiceTest(GenerateInvoiceTest):
    use_pricing_point = False
    use_reimbursement_point = False


class PrepareInvoiceContextTest:
    use_pricing_point = True
    use_reimbursement_point = True

    @auto_override_features
    def test_context(self):
        business_unit, reimbursement_point, stocks, _venue = invoice_test_data(self.use_reimbursement_point)
        bookings = []
        user = create_rich_user()
        for stock in stocks:
            booking = bookings_factories.UsedIndividualBookingFactory(
                stock=stock,
                individualBooking__user=user,
            )
            bookings.append(booking)
        for booking in bookings[:3]:
            api.price_booking(booking, self.use_pricing_point)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        for booking in bookings[3:]:
            api.price_booking(booking, self.use_pricing_point)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        cashflow_ids = [c.id for c in models.Cashflow.query.all()]
        invoice = api._generate_invoice(
            business_unit_id=None if self.use_reimbursement_point else business_unit.id,
            reimbursement_point_id=reimbursement_point.id if self.use_reimbursement_point else None,
            cashflow_ids=cashflow_ids,
        )

        context = api._prepare_invoice_context(invoice, self.use_reimbursement_point)

        general, books, not_reimbursed, custom = tuple(g for g in context["groups"])
        assert general.used_bookings_subtotal == 2006130
        assert general.contribution_subtotal == 406
        assert general.reimbursed_amount_subtotal == -2005724

        assert books.used_bookings_subtotal == 6000
        assert books.contribution_subtotal == 200
        assert books.reimbursed_amount_subtotal == -5800

        assert not_reimbursed.used_bookings_subtotal == 5800
        assert not_reimbursed.contribution_subtotal == 5800
        assert not_reimbursed.reimbursed_amount_subtotal == 0

        assert custom.used_bookings_subtotal == 4300
        assert custom.contribution_subtotal == 220
        assert custom.reimbursed_amount_subtotal == -4080

        assert context["invoice"] == invoice
        assert context["total_used_bookings_amount"] == 2022230
        assert context["total_contribution_amount"] == 6626
        assert context["total_reimbursed_amount"] == -2015604

    def test_get_invoice_period_second_half(self):
        start_period, end_period = api.get_invoice_period(datetime.datetime(2020, 3, 4))
        assert start_period == datetime.datetime(2020, 2, 16)
        assert end_period == datetime.datetime(2020, 2, 29)

    def test_get_invoice_period_first_half(self):
        start_period, end_period = api.get_invoice_period(datetime.datetime(2020, 3, 27))
        assert start_period == datetime.datetime(2020, 3, 1)
        assert end_period == datetime.datetime(2020, 3, 15)


class LegacyPrepareInvoiceContextTest(PrepareInvoiceContextTest):
    use_pricing_point = False
    use_reimbursement_point = False


class GenerateInvoiceHtmlTest:
    TEST_FILES_PATH = pathlib.Path(tests.__path__[0]) / "files"
    use_pricing_point = True
    use_reimbursement_point = True

    def generate_and_compare_invoice(self, stocks, business_unit, reimbursement_point, venue):
        bookings = []
        user = create_rich_user()
        for stock in stocks:
            booking = bookings_factories.UsedIndividualBookingFactory(
                stock=stock,
                individualBooking__user=user,
            )
            bookings.append(booking)
        for booking in bookings[:3]:
            api.price_booking(booking, self.use_pricing_point)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        for booking in bookings[3:]:
            api.price_booking(booking, self.use_pricing_point)
        duo_offer = offers_factories.OfferFactory(venue=venue, isDuo=True)
        duo_stock = offers_factories.StockFactory(offer=duo_offer, price=1)
        duo_booking = bookings_factories.UsedIndividualBookingFactory(stock=duo_stock, quantity=2)
        api.price_booking(duo_booking, self.use_pricing_point)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        cashflows = models.Cashflow.query.order_by(models.Cashflow.id).all()
        cashflow_ids = [c.id for c in cashflows]
        invoice = api._generate_invoice(
            business_unit_id=None if self.use_reimbursement_point else business_unit.id,
            reimbursement_point_id=reimbursement_point.id if self.use_reimbursement_point else None,
            cashflow_ids=cashflow_ids,
        )

        invoice_html = api._generate_invoice_html(invoice, self.use_reimbursement_point)

        with open(self.TEST_FILES_PATH / "invoice" / "rendered_invoice.html", "r", encoding="utf-8") as f:
            expected_invoice_html = f.read()
        # We need to replace Cashflow IDs and dates that were used when generating the expected html
        expected_invoice_html = expected_invoice_html.replace(
            '<td class="cashflow_batch_label">1</td>',
            f'<td class="cashflow_batch_label">{cashflows[0].batch.label}</td>',
        )
        expected_invoice_html = expected_invoice_html.replace(
            '<td class="cashflow_batch_label">2</td>',
            f'<td class="cashflow_batch_label">{cashflows[1].batch.label}</td>',
        )
        expected_invoice_html = expected_invoice_html.replace(
            '<td class="cashflow_creation_date">21/12/2021</td>',
            f'<td class="cashflow_creation_date">{invoice.date.strftime("%d/%m/%Y")}</td>',
        )
        expected_invoice_html = expected_invoice_html.replace(
            'content: "Relevé n°F220000001 du 30/01/2022";',
            f'content: "Relevé n°F220000001 du {invoice.date.strftime("%d/%m/%Y")}";',
        )
        start_period, end_period = api.get_invoice_period(invoice.date)
        expected_invoice_html = expected_invoice_html.replace(
            "Remboursement des réservations validées entre le 01/01/22 et le 14/01/22, sauf cas exceptionnels",
            f'Remboursement des réservations validées entre le {start_period.strftime("%d/%m/%y")} et le {end_period.strftime("%d/%m/%y")}, sauf cas exceptionnels',
        )
        if self.use_reimbursement_point:
            expected_invoice_html = expected_invoice_html.replace("\n    <p><b>SIRET :</b> 85331845900023</p>", "")
        assert expected_invoice_html == invoice_html

    @auto_override_features
    def test_basics(self):
        business_unit, reimbursement_point, stocks, venue = invoice_test_data(self.use_reimbursement_point)
        if self.use_reimbursement_point:
            pricing_point = offerers_models.Venue.query.get(venue.current_pricing_point_id)
        else:
            pricing_point = None
        only_educational_venue = offerers_factories.VenueFactory(
            name="Coiffeur collecTIF",
            businessUnit=business_unit,
            pricing_point=pricing_point,
            reimbursement_point=reimbursement_point,
        )
        only_educational_booking = bookings_factories.UsedEducationalBookingFactory(
            stock__price=666,
            stock__offer__venue=only_educational_venue,
            stock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
        educational_booking1 = bookings_factories.UsedEducationalBookingFactory(
            stock__price=5000,
            stock__offer__venue=venue,
            stock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
        educational_booking2 = bookings_factories.UsedEducationalBookingFactory(
            stock__price=250,
            stock__offer__venue=venue,
            stock__beginningDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=1),
        )
        api.price_booking(educational_booking1, self.use_pricing_point)
        api.price_booking(educational_booking2, self.use_pricing_point)
        api.price_booking(only_educational_booking, self.use_pricing_point)

        self.generate_and_compare_invoice(stocks, business_unit, reimbursement_point, venue)

    @auto_override_features
    def test_basics_with_new_collective_model(self):
        business_unit, reimbursement_point, stocks, venue = invoice_test_data(self.use_reimbursement_point)
        if self.use_reimbursement_point:
            pricing_point = offerers_models.Venue.query.get(venue.current_pricing_point_id)
        else:
            pricing_point = None
        only_collective_venue = offerers_factories.VenueFactory(
            businessUnit=business_unit,
            pricing_point=pricing_point,
            reimbursement_point=reimbursement_point,
            name="Coiffeur collecTIF",
        )
        only_collective_booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__beginningDatetime=datetime.datetime.utcnow(),
            collectiveStock__collectiveOffer__venue=only_collective_venue,
            collectiveStock__price=666,
        )
        collective_booking = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__beginningDatetime=datetime.datetime.utcnow(),
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__price=5000,
        )
        collective_booking2 = educational_factories.UsedCollectiveBookingFactory(
            collectiveStock__beginningDatetime=datetime.datetime.utcnow(),
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__price=250,
        )
        api.price_booking(collective_booking, self.use_pricing_point)
        api.price_booking(collective_booking2, self.use_pricing_point)
        api.price_booking(only_collective_booking, self.use_pricing_point)

        self.generate_and_compare_invoice(stocks, business_unit, reimbursement_point, venue)


class LegacyGenerateInvoiceHtmlTest(GenerateInvoiceHtmlTest):
    use_pricing_point = False
    use_reimbursement_point = False


class StoreInvoicePdfTest:
    STORAGE_DIR = pathlib.Path(tests.__path__[0]) / ".." / "src" / "pcapi" / "static" / "object_store_data"
    INVOICES_DIR = STORAGE_DIR / "invoices"

    @override_settings(OBJECT_STORAGE_URL=STORAGE_DIR)
    def test_basics(self, clear_tests_invoices_bucket):
        invoice = factories.InvoiceFactory()
        html = "<p>Trust me, I am an invoice.<p>"
        existing_number_of_files = len(recursive_listdir(self.INVOICES_DIR))
        api._store_invoice_pdf(invoice.storage_object_id, html)

        assert invoice.url == f"{self.INVOICES_DIR}/{invoice.storage_object_id}"
        assert len(recursive_listdir(self.INVOICES_DIR)) == existing_number_of_files + 2
        assert (self.INVOICES_DIR / f"{invoice.storage_object_id}").exists()
        assert (self.INVOICES_DIR / f"{invoice.storage_object_id}.type").exists()


class GenerateAndStoreInvoiceTest:
    STORAGE_DIR = pathlib.Path(tests.__path__[0]) / ".." / "src" / "pcapi" / "static" / "object_store_data"
    use_pricing_point = True
    use_reimbursement_point = True

    @override_settings(OBJECT_STORAGE_URL=STORAGE_DIR)
    @auto_override_features
    # FIXME (dbaty, 2022-07-22): this test should use the
    # "clear_tests_invoices_bucket" fixture, but I cannot make
    # it work with the "auto_override_features" decorator. The
    # fixture should be added back when we remove the decorator.
    def test_basics(self):
        if self.use_reimbursement_point:
            reimbursement_point = offerers_factories.VenueFactory()
        else:
            venue = offerers_factories.VenueFactory()
            business_unit = venue.businessUnit

        # We're not interested in the invoice itself. We just want to
        # check that the function does not fail and that the e-mail is
        # sent.
        api.generate_and_store_invoice(
            business_unit_id=None if self.use_reimbursement_point else business_unit.id,
            reimbursement_point_id=reimbursement_point.id if self.use_reimbursement_point else None,
            cashflow_ids=[1],
            use_reimbursement_point=self.use_reimbursement_point,
        )

        assert len(mails_testing.outbox) == 1


class LegacyGenerateAndStoreInvoiceTest(GenerateAndStoreInvoiceTest):
    use_pricing_point = False
    use_reimbursement_point = False


def test_merge_cashflow_batches():
    # Set BusinessUnit.siret to avoid clash when PricingFactory
    # creates a Venue with SIRET "000...000" and then tries to create
    # a business unit with the same SIRET again.
    bu1 = factories.BusinessUnitFactory(siret="1")
    bu2 = factories.BusinessUnitFactory(siret="2")
    bu3 = factories.BusinessUnitFactory(siret="3")
    bu4 = factories.BusinessUnitFactory(siret="4")
    bu5 = factories.BusinessUnitFactory(siret="5")
    batch1 = factories.CashflowBatchFactory(id=1)
    batch2 = factories.CashflowBatchFactory(id=2)
    batch3 = factories.CashflowBatchFactory(id=3)
    batch4 = factories.CashflowBatchFactory(id=4)
    batch5 = factories.CashflowBatchFactory(id=5)

    # Cashflow of batches 1 and 2: should not be changed.
    factories.CashflowFactory(batch=batch1, businessUnit=bu1, amount=10)
    factories.CashflowFactory(batch=batch2, businessUnit=bu1, amount=20)
    # Business unit 1: batches 3, 4 and 5.
    factories.CashflowFactory(batch=batch3, businessUnit=bu1, amount=40)
    factories.CashflowFactory(batch=batch4, businessUnit=bu1, amount=80)
    factories.CashflowFactory(batch=batch5, businessUnit=bu1, amount=160)
    # Business unit 2: batches 3 and 4.
    cf_3_2 = factories.CashflowFactory(batch=batch3, businessUnit=bu2, amount=320)
    factories.PricingFactory(cashflows=[cf_3_2])
    cf_4_2 = factories.CashflowFactory(batch=batch4, businessUnit=bu2, amount=640)
    factories.PricingFactory(cashflows=[cf_4_2])
    # Business unit 3: batches 3 and 5.
    cf_3_3 = factories.CashflowFactory(batch=batch3, businessUnit=bu3, amount=1280)
    factories.PricingFactory(cashflows=[cf_3_3])
    cf_5_3 = factories.CashflowFactory(batch=batch5, businessUnit=bu3, amount=2560)
    factories.PricingFactory(cashflows=[cf_5_3])
    # Business unit 4: batch 3 only
    cf_3_4 = factories.CashflowFactory(batch=batch3, businessUnit=bu4, amount=5120)
    factories.PricingFactory(cashflows=[cf_3_4])
    # Business unit 5: batch 5 (nothing to do)
    cf_5_5 = factories.CashflowFactory(batch=batch5, businessUnit=bu5, amount=10240)
    factories.PricingFactory(cashflows=[cf_5_5])

    def get_cashflows(batch_id, business_unit=None):
        query = models.Cashflow.query.filter_by(batchId=batch_id)
        if business_unit:
            query = query.filter_by(businessUnitId=business_unit.id)
        return query.all()

    api.merge_cashflow_batches(batches_to_remove=[batch3, batch4], target_batch=batch5)

    # No changes on batches 1 and 2.
    cashflows = get_cashflows(batch_id=1)
    assert len(cashflows) == 1
    assert cashflows[0].businessUnit == bu1
    assert cashflows[0].amount == 10
    cashflows = get_cashflows(batch_id=2)
    assert len(cashflows) == 1
    assert cashflows[0].businessUnit == bu1
    assert cashflows[0].amount == 20

    # Batches 3 and 4 have been deleted.
    assert not models.CashflowBatch.query.filter(models.CashflowBatch.id.in_((3, 4))).all()

    # Batch 5 now has all cashflows.
    assert len(get_cashflows(batch_id=5)) == 5
    assert get_cashflows(batch_id=5, business_unit=bu1)[0].amount == 40 + 80 + 160
    assert get_cashflows(batch_id=5, business_unit=bu2)[0].amount == 320 + 640
    assert get_cashflows(batch_id=5, business_unit=bu3)[0].amount == 1280 + 2560
    assert get_cashflows(batch_id=5, business_unit=bu4)[0].amount == 5120
    assert get_cashflows(batch_id=5, business_unit=bu5)[0].amount == 10240


def test_get_drive_folder_name():
    cutoff = datetime.datetime(2022, 4, 30, 22, 0)
    batch = factories.CashflowBatchFactory(cutoff=cutoff)
    name = api._get_drive_folder_name(batch.id)
    assert name == "2022-04 - jusqu'au 30 avril"
