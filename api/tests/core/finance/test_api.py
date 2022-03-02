import csv
import datetime
from decimal import Decimal
import io
import pathlib
from unittest import mock
import zipfile

import pytest
import pytz
import sqlalchemy.orm as sqla_orm

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.finance import api
from pcapi.core.finance import exceptions
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.object_storage.testing import recursive_listdir
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import clean_temporary_files
from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
from pcapi.models.bank_information import BankInformationStatus
from pcapi.utils import human_ids

import tests


pytestmark = pytest.mark.usefixtures("db_session")


def create_booking_with_undeletable_dependent(date_used=None):
    if not date_used:
        date_used = datetime.datetime.utcnow()
    booking = bookings_factories.UsedBookingFactory(dateUsed=date_used)
    factories.PricingFactory(
        siret=booking.venue.siret,
        valueDate=booking.dateUsed + datetime.timedelta(seconds=1),
        status=models.PricingStatus.PROCESSED,
    )
    return booking


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

    def test_return_value_sent_if_not_string(self):
        number = 1
        result = api._clean_for_accounting(number)
        assert result == 1


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
        assert pricing.siret == booking.venue.siret
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

    def test_price_free_booking(self):
        booking = bookings_factories.UsedBookingFactory(
            amount=0,
            stock=offers_factories.ThingStockFactory(),
        )
        pricing = api.price_booking(booking)
        assert models.Pricing.query.count() == 1
        assert pricing.amount == 0

    def test_accrue_revenue(self):
        booking1 = bookings_factories.UsedBookingFactory(amount=10)
        booking2 = bookings_factories.UsedBookingFactory(
            amount=20,
            stock__offer__venue=booking1.venue,
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
            stock__offer__venue=booking1.venue,
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

    def test_price_booking_checks_business_unit(self):
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue__businessUnit__siret=None)
        pricing = api.price_booking(booking)
        assert pricing is None

    def test_price_booking_ignores_missing_bank_information(self):
        booking = bookings_factories.UsedBookingFactory(
            stock__offer__venue__businessUnit__bankAccount__status=BankInformationStatus.DRAFT,
        )
        pricing = api.price_booking(booking)
        assert pricing

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
        venue = offers_factories.VenueFactory(siret="123456")
        booking1 = bookings_factories.UsedBookingFactory(stock__offer__venue=venue, amount=20)
        _pricing1 = factories.PricingFactory(booking=booking1)
        booking2 = bookings_factories.UsedBookingFactory(stock__offer__venue=venue)
        _pricing_other = factories.PricingFactory()

        siret, current_revenue = api._get_siret_and_current_revenue(booking2)
        assert siret == "123456"
        assert current_revenue == 2000

    def test_use_business_unit_siret(self):
        venue = offers_factories.VirtualVenueFactory(siret=None, businessUnit__siret="654321")
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue=venue, amount=20)

        siret, current_revenue = api._get_siret_and_current_revenue(booking)
        assert siret == "654321"
        assert current_revenue == 0

    def test_use_booking_quantity(self):
        venue = offers_factories.VenueFactory(siret="123456")
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
        pricing = factories.PricingFactory(status=models.PricingStatus.PROCESSED)
        with pytest.raises(exceptions.NonCancellablePricingError):
            api.cancel_pricing(pricing.booking, models.PricingLogReason.MARK_AS_UNUSED)
        pricing = models.Pricing.query.one()
        assert pricing.status == models.PricingStatus.PROCESSED  # unchanged

    def test_cancel_with_dependent_booking(self):
        pricing = factories.PricingFactory()
        _dependent_pricing = factories.PricingFactory(
            siret=pricing.siret,
            valueDate=pricing.valueDate + datetime.timedelta(seconds=1),
        )
        pricing = api.cancel_pricing(pricing.booking, models.PricingLogReason.MARK_AS_UNUSED)
        assert pricing.status == models.PricingStatus.CANCELLED
        assert models.Pricing.query.one() == pricing


class DeleteDependentPricingsTest:
    def test_basics(self):
        used_date = datetime.datetime(2022, 1, 15)
        booking = bookings_factories.UsedBookingFactory(dateUsed=used_date)
        earlier_pricing = factories.PricingFactory(
            siret=booking.venue.siret,
            valueDate=booking.dateUsed - datetime.timedelta(seconds=1),
        )
        later_pricing = factories.PricingFactory(
            siret=booking.venue.siret,
            valueDate=booking.dateUsed + datetime.timedelta(seconds=1),
        )
        later_pricing_another_year = factories.PricingFactory(
            siret=booking.venue.siret,
            valueDate=used_date + datetime.timedelta(days=365),
        )
        factories.PricingLineFactory(pricing=later_pricing)
        factories.PricingLogFactory(pricing=later_pricing)
        _same_date_pricing_but_greater_booking_id = factories.PricingFactory(
            siret=booking.venue.siret,
            valueDate=booking.dateUsed,
        )
        api._delete_dependent_pricings(booking, "some log message")
        kept = [earlier_pricing, later_pricing_another_year]
        assert list(models.Pricing.query.all()) == kept

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
        api.price_bookings(min_date=self.few_minutes_ago)
        assert len(booking.pricings) == 1

    @mock.patch("pcapi.core.finance.api.price_booking", lambda booking: None)
    def test_num_queries(self):
        bookings_factories.UsedBookingFactory(dateUsed=self.few_minutes_ago)
        n_queries = 1
        with assert_num_queries(n_queries):
            api.price_bookings(self.few_minutes_ago)

    def test_error_on_a_booking_does_not_block_other_bookings(self):
        booking1 = create_booking_with_undeletable_dependent(date_used=self.few_minutes_ago)
        booking2 = bookings_factories.UsedBookingFactory(dateUsed=self.few_minutes_ago)

        api.price_bookings(self.few_minutes_ago)

        assert not booking1.pricings
        assert len(booking2.pricings) == 1

    def test_price_even_without_accepted_bank_info(self):
        booking = bookings_factories.UsedBookingFactory(
            dateUsed=self.few_minutes_ago,
            stock__offer__venue__businessUnit__bankAccount__status=BankInformationStatus.DRAFT,
        )
        api.price_bookings(min_date=self.few_minutes_ago)
        assert len(booking.pricings) == 1


class GenerateCashflowsTest:
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
        pricing2 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__beginningDatetime=now - datetime.timedelta(days=1),
            amount=-3000,
        )
        pricing_future_event = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            booking__stock__beginningDatetime=now + datetime.timedelta(days=1),
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
        assert models.Cashflow.query.count() == 2
        assert len(pricing11.cashflows) == 1
        assert len(pricing12.cashflows) == 1
        assert pricing11.cashflows[0] == pricing12.cashflows[0]
        assert pricing11.cashflows[0].amount == -2000
        assert pricing11.cashflows[0].bankAccount == business_unit1.bankAccount
        assert pricing2.cashflows[0].amount == -3000

        assert not pricing_future_event.cashflows
        assert not pricing_no_bank_account.cashflows
        assert not pricing_pending.cashflows
        assert not pricing_after_cutoff.cashflows

    def test_no_cashflow_if_total_is_zero(self):
        business_unit1 = factories.BusinessUnitFactory()
        _pricing_total_is_zero_1 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            businessUnit=business_unit1,
            amount=-1000,
        )
        _pricing_total_is_zero_2 = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            businessUnit=business_unit1,
            amount=1000,
        )
        _pricing_free_offer = factories.PricingFactory(
            status=models.PricingStatus.VALIDATED,
            businessUnit=business_unit1,
            amount=0,
        )
        cutoff = datetime.datetime.utcnow()
        api.generate_cashflows(cutoff)
        assert models.Cashflow.query.count() == 0

    def test_no_cashflow_if_no_accepted_bank_information(self):
        business_unit1 = factories.BusinessUnitFactory(bankAccount__status=BankInformationStatus.DRAFT)
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

    def test_assert_num_queries(self):
        business_unit1 = factories.BusinessUnitFactory()
        factories.PricingFactory(status=models.PricingStatus.VALIDATED, businessUnit=business_unit1)
        factories.PricingFactory(status=models.PricingStatus.VALIDATED, businessUnit=business_unit1)
        factories.PricingFactory(status=models.PricingStatus.VALIDATED)
        cutoff = datetime.datetime.utcnow()

        n_queries = 0
        n_queries += 1  # insert CashflowBatch
        n_queries += 1  # commit
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


@clean_temporary_files
def test_generate_payment_files():
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


@clean_temporary_files
def test_generate_business_units_file():
    venue1 = offers_factories.VenueFactory(
        name='Venue 1 only name "doublequote" \n',
        publicName=None,
        siret='siret 1 "t"',
        businessUnit__name=' Business unit 1 "doublequote"\n',
        businessUnit__bankAccount__bic='bic 1 "t"\n',
        businessUnit__bankAccount__iban='iban 1 "t"\n',
    )
    business_unit1 = venue1.businessUnit
    offers_factories.VenueFactory(businessUnit=business_unit1)
    venue2 = offers_factories.VenueFactory(
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

    reader = csv.DictReader(path.open(), quoting=csv.QUOTE_NONNUMERIC)
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
def test_generate_payments_file():
    used_date = datetime.datetime(2020, 1, 2)
    # This pricing belong to a business unit whose venue is the same
    # as the venue of the offer.
    venue1 = offers_factories.VenueFactory(
        name='Le Petit Rintintin "test"\n',
        siret='123456 "test"\n',
    )
    pricing1 = factories.PricingFactory(
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
    business_unit_venue2 = offers_factories.VenueFactory(
        siret="22222222233333",
        name="BU du Gigantesque Cubitus\n",
    )
    business_unit2 = business_unit_venue2.businessUnit
    offer_venue2 = offers_factories.VenueFactory(
        name="Le Gigantesque Cubitus\n",
        siret="99999999999999",
        businessUnit=business_unit2,
    )
    pricing2 = factories.PricingFactory(
        amount=-900,  # rate = 75 %
        booking__amount=12,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire plutôt bien",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=offer_venue2,
    )
    pricing3 = factories.PricingFactory(
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
    pricing4 = factories.PricingFactory(
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
    cutoff = datetime.datetime.utcnow()
    batch_id = api.generate_cashflows(cutoff)

    n_queries = 1  # select pricings
    with assert_num_queries(n_queries):
        path = api._generate_payments_file(batch_id)

    with zipfile.ZipFile(path) as zfile:
        with zfile.open("payment_details.csv") as csv_bytefile:
            csv_textfile = io.TextIOWrapper(csv_bytefile)
            reader = csv.DictReader(csv_textfile, quoting=csv.QUOTE_NONNUMERIC)
            rows = list(reader)
    assert len(rows) == 4
    assert rows[0] == {
        "Identifiant de la BU": human_ids.humanize(venue1.id),
        "SIRET de la BU": "123456 test",
        "Libellé de la BU": "Le Petit Rintintin test",
        "Identifiant du lieu": human_ids.humanize(venue1.id),
        "Libellé du lieu": "Le Petit Rintintin test",
        "Identifiant de l'offre": pricing1.booking.stock.offerId,
        "Nom de l'offre": "Une histoire formidable",
        "Sous-catégorie de l'offre": "SUPPORT_PHYSIQUE_FILM",
        "Prix de la réservation": 10,
        "Type de réservation": "PC",
        "Date de validation": "2020-01-02 00:00:00",
        "Identifiant de la valorisation": pricing1.id,
        "Taux de remboursement": 1,
        "Montant remboursé à l'offreur": 10,
    }
    assert rows[1] == {
        "Identifiant de la BU": human_ids.humanize(business_unit_venue2.id),
        "SIRET de la BU": "22222222233333",
        "Libellé de la BU": "BU du Gigantesque Cubitus",
        "Identifiant du lieu": human_ids.humanize(offer_venue2.id),
        "Libellé du lieu": "Le Gigantesque Cubitus",
        "Identifiant de l'offre": pricing2.booking.stock.offerId,
        "Nom de l'offre": "Une histoire plutôt bien",
        "Sous-catégorie de l'offre": "SUPPORT_PHYSIQUE_FILM",
        "Prix de la réservation": 12,
        "Type de réservation": "PC",
        "Date de validation": "2020-01-02 00:00:00",
        "Identifiant de la valorisation": pricing2.id,
        "Taux de remboursement": 0.75,
        "Montant remboursé à l'offreur": 9,
    }
    assert rows[2] == {
        "Identifiant de la BU": human_ids.humanize(business_unit_venue2.id),
        "SIRET de la BU": "22222222233333",
        "Libellé de la BU": "BU du Gigantesque Cubitus",
        "Identifiant du lieu": human_ids.humanize(offer_venue2.id),
        "Libellé du lieu": "Le Gigantesque Cubitus",
        "Identifiant de l'offre": pricing3.booking.stock.offerId,
        "Nom de l'offre": "Une histoire plutôt bien",
        "Sous-catégorie de l'offre": "SUPPORT_PHYSIQUE_FILM",
        "Prix de la réservation": 12,
        "Type de réservation": "PC",
        "Date de validation": "2020-01-02 00:00:00",
        "Identifiant de la valorisation": pricing3.id,
        "Taux de remboursement": 0.50,
        "Montant remboursé à l'offreur": 6,
    }
    assert rows[3] == {
        "Identifiant de la BU": human_ids.humanize(business_unit_venue2.id),
        "SIRET de la BU": "22222222233333",
        "Libellé de la BU": "BU du Gigantesque Cubitus",
        "Identifiant du lieu": human_ids.humanize(offer_venue2.id),
        "Libellé du lieu": "Le Gigantesque Cubitus",
        "Identifiant de l'offre": pricing4.booking.stock.offerId,
        "Nom de l'offre": "Une histoire plutôt bien",
        "Sous-catégorie de l'offre": "SUPPORT_PHYSIQUE_FILM",
        "Prix de la réservation": 12,
        "Type de réservation": "EACI",
        "Date de validation": "2020-01-02 00:00:00",
        "Identifiant de la valorisation": pricing4.id,
        "Taux de remboursement": 0.50,
        "Montant remboursé à l'offreur": 6,
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
def test_genererate_invoice_file():
    first_siret = "12345678900"
    business_unit1 = factories.BusinessUnitFactory(siret=first_siret)
    venue1 = offers_factories.VenueFactory(businessUnit=business_unit1, siret=first_siret)

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
    offers_factories.VenueFactory(businessUnit=business_unit2, siret=second_siret)

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

    path = api.generate_invoice_file()
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
        )
        business_unit = venue.businessUnit

        api.edit_business_unit(business_unit, siret="12345678901234")

        business_unit = models.BusinessUnit.query.one()
        assert business_unit.siret == "12345678901234"

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


@pytest.fixture(name="invoice_data")
def invoice_test_data():
    venue = offers_factories.VenueFactory(
        siret="85331845900023",
        bookingEmail="pro@example.com",
        businessUnit__name="SARL LIBRAIRIE BOOKING",
        businessUnit__bankAccount__iban="FR2710010000000000000000064",
    )

    business_unit = venue.businessUnit
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
    return business_unit, stocks


class GenerateInvoicesTest:
    # Mock slow functions that we are not interested in.
    @mock.patch("pcapi.core.finance.api._generate_invoice_html")
    @mock.patch("pcapi.core.finance.api._store_invoice_pdf")
    def test_basics(self, _mocked1, _mocked2):
        booking1 = bookings_factories.UsedIndividualBookingFactory()
        booking2 = bookings_factories.UsedIndividualBookingFactory()
        booking3 = bookings_factories.UsedIndividualBookingFactory(stock=booking1.stock)
        booking4 = bookings_factories.UsedIndividualBookingFactory()
        # Cashflows for booking1 and booking2 will be UNDER_REVIEW.
        api.price_booking(booking1)
        api.price_booking(booking2)
        api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())

        # Another cashflow for booking3 that has the same business
        # Unit as booking2.
        api.price_booking(booking3)
        api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())

        # Cashflow for booking4 will still be PENDING. No invoice
        # should be generated.
        api.price_booking(booking4)
        api.generate_cashflows(datetime.datetime.utcnow())

        api.generate_invoices()

        invoices = models.Invoice.query.all()
        assert len(invoices) == 2
        invoiced_bookings = {inv.cashflows[0].pricings[0].booking for inv in invoices}
        assert invoiced_bookings == {booking1, booking2}


class GenerateInvoiceTest:
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
        + 1  # commit
    )

    def test_reference_scheme_increments(self):
        venue = offers_factories.VenueFactory(siret="85331845900023")
        business_unit = venue.businessUnit
        invoice = api._generate_invoice(business_unit_id=business_unit.id, cashflow_ids=[1, 2])
        second_invoice = api._generate_invoice(business_unit_id=business_unit.id, cashflow_ids=[1, 2])

        assert invoice.reference == "F220000001"
        assert second_invoice.reference == "F220000002"

    def test_one_regular_rule_one_rate(self):
        venue = offers_factories.VenueFactory(siret="85331845900023")
        business_unit = venue.businessUnit
        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=20)
        booking1 = bookings_factories.UsedBookingFactory(stock=stock)
        booking2 = bookings_factories.UsedBookingFactory(stock=stock)
        api.price_booking(booking1)
        api.price_booking(booking2)
        api.generate_cashflows(datetime.datetime.utcnow())
        cashflows = (
            models.Cashflow.query.join(models.Cashflow.pricings)
            .filter(models.Pricing.businessUnitId == business_unit.id)
            .all()
        )
        cashflow_ids = [c.id for c in cashflows]
        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(business_unit_id=business_unit.id, cashflow_ids=cashflow_ids)

        assert invoice.reference == "F220000001"
        assert invoice.businessUnit == business_unit
        assert invoice.amount == -40 * 100
        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème général", "position": 1}
        assert line.contributionAmount == 0
        assert line.reimbursedAmount == -40 * 100
        assert line.rate == 1
        assert line.label == "Montant remboursé"

    def test_two_regular_rules_two_rates(self):
        venue = offers_factories.VenueFactory(siret="85331845900023")
        business_unit = venue.businessUnit
        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock1 = offers_factories.ThingStockFactory(offer=offer, price=19_850)
        stock2 = offers_factories.ThingStockFactory(offer=offer, price=160)
        booking1 = bookings_factories.UsedBookingFactory(stock=stock1)
        booking2 = bookings_factories.UsedBookingFactory(stock=stock2)
        api.price_booking(booking1)
        api.price_booking(booking2)
        api.generate_cashflows(datetime.datetime.utcnow())
        cashflows = (
            models.Cashflow.query.join(models.Cashflow.pricings)
            .filter(models.Pricing.businessUnitId == business_unit.id)
            .all()
        )
        cashflow_ids = [c.id for c in cashflows]

        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(business_unit_id=business_unit.id, cashflow_ids=cashflow_ids)

        assert invoice.reference == "F220000001"
        assert invoice.businessUnit == business_unit
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

    def test_one_custom_rule(self):
        venue = offers_factories.VenueFactory(siret="85331845900023")
        business_unit = venue.businessUnit
        offer = offers_factories.ThingOfferFactory(venue=venue)
        stock = offers_factories.ThingStockFactory(offer=offer, price=23)
        payments_factories.CustomReimbursementRuleFactory(amount=22, offer=offer)
        booking1 = bookings_factories.UsedBookingFactory(stock=stock)
        booking2 = bookings_factories.UsedBookingFactory(stock=stock)
        api.price_booking(booking1)
        api.price_booking(booking2)
        api.generate_cashflows(datetime.datetime.utcnow())
        cashflows = (
            models.Cashflow.query.join(models.Cashflow.pricings)
            .filter(models.Pricing.businessUnitId == business_unit.id)
            .all()
        )
        cashflow_ids = [c.id for c in cashflows]

        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(business_unit_id=business_unit.id, cashflow_ids=cashflow_ids)

        assert invoice.reference == "F220000001"
        assert invoice.businessUnit == business_unit
        assert invoice.amount == -4400
        assert len(invoice.lines) == 1
        line = invoice.lines[0]
        assert line.group == {"label": "Barème dérogatoire", "position": 4}
        assert line.contributionAmount == 200
        assert line.reimbursedAmount == -4400
        assert line.rate == Decimal("0.9565")
        assert line.label == "Montant remboursé"

    def test_many_rules_and_rates_two_cashflows(self, invoice_data):
        business_unit, stocks = invoice_data
        bookings = []
        for stock in stocks:
            booking = bookings_factories.UsedBookingFactory(stock=stock)
            bookings.append(booking)
        for booking in bookings[:3]:
            api.price_booking(booking)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        for booking in bookings[3:]:
            api.price_booking(booking)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        cashflows = (
            models.Cashflow.query.join(models.Cashflow.pricings)
            .filter(models.Pricing.businessUnitId == business_unit.id)
            .all()
        )
        cashflow_ids = [c.id for c in cashflows]

        with assert_num_queries(self.EXPECTED_NUM_QUERIES):
            invoice = api._generate_invoice(business_unit_id=business_unit.id, cashflow_ids=cashflow_ids)

        assert len(invoice.cashflows) == 2
        assert invoice.reference == "F220000001"
        assert invoice.businessUnit == business_unit
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

    def test_update_statuses(self):
        booking = bookings_factories.UsedBookingFactory()
        business_unit_id = booking.venue.businessUnitId
        api.price_booking(booking)
        api.generate_cashflows(datetime.datetime.utcnow())
        cashflow_ids = {cf.id for cf in models.Cashflow.query.all()}
        api._generate_invoice(business_unit_id, cashflow_ids)

        get_statuses = lambda model: {s for s, in model.query.with_entities(getattr(model, "status"))}
        cashflow_statuses = get_statuses(models.Cashflow)
        assert cashflow_statuses == {models.CashflowStatus.ACCEPTED}
        pricing_statuses = get_statuses(models.Pricing)
        assert pricing_statuses == {models.PricingStatus.INVOICED}
        booking_statuses = get_statuses(bookings_models.Booking)
        assert booking_statuses == {bookings_models.BookingStatus.REIMBURSED}


class PrepareInvoiceContextTest:
    def test_context(self, invoice_data):
        business_unit, stocks = invoice_data
        bookings = []
        for stock in stocks:
            booking = bookings_factories.UsedBookingFactory(stock=stock)
            bookings.append(booking)
        for booking in bookings[:3]:
            api.price_booking(booking)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        for booking in bookings[3:]:
            api.price_booking(booking)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        cashflows = (
            models.Cashflow.query.join(models.Cashflow.pricings)
            .filter(models.Pricing.businessUnitId == business_unit.id)
            .all()
        )
        cashflow_ids = [c.id for c in cashflows]
        invoice = api._generate_invoice(business_unit_id=business_unit.id, cashflow_ids=cashflow_ids)
        context = api._prepare_invoice_context(invoice)
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


class GenerateInvoiceHtmlTest:
    TEST_FILES_PATH = pathlib.Path(tests.__path__[0]) / "files"

    def test_basics(self, invoice_data):
        business_unit, stocks = invoice_data
        bookings = []
        for stock in stocks:
            booking = bookings_factories.UsedBookingFactory(stock=stock)
            bookings.append(booking)
        for booking in bookings[:3]:
            api.price_booking(booking)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        for booking in bookings[3:]:
            api.price_booking(booking)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        cashflows = (
            models.Cashflow.query.join(models.Cashflow.pricings)
            .filter(models.Pricing.businessUnitId == business_unit.id)
            .all()
        )
        cashflow_ids = [c.id for c in cashflows]
        invoice = api._generate_invoice(business_unit_id=business_unit.id, cashflow_ids=cashflow_ids)

        invoice_html = api._generate_invoice_html(invoice)

        with open(self.TEST_FILES_PATH / "invoice" / "rendered_invoice.html", "r") as f:
            expected_invoice_html = f.read()
        # We need to replace Cashflow IDs and dates that were used when generating the expected html
        expected_invoice_html = expected_invoice_html.replace(
            '<td class="cashflow_id">1</td>', f'<td class="cashflow_id">{cashflow_ids[0]}</td>'
        )
        expected_invoice_html = expected_invoice_html.replace(
            '<td class="cashflow_id">2</td>', f'<td class="cashflow_id">{cashflow_ids[1]}</td>'
        )
        expected_invoice_html = expected_invoice_html.replace(
            '<td class="cashflow_creation_date">21/12/2021</td>',
            f'<td class="cashflow_creation_date">{cashflows[0].creationDate.strftime("%d/%m/%Y")}</td>',
        )
        expected_invoice_html = expected_invoice_html.replace(
            'content: "Relevé n°F220000001 du 30/01/2022";',
            f'content: "Relevé n°F220000001 du {invoice.date.strftime("%d/%m/%Y")}";',
        )
        assert expected_invoice_html == invoice_html


class StoreInvoicePdfTest:
    BASE_THUMBS_DIR = pathlib.Path(tests.__path__[0]) / ".." / "src" / "pcapi" / "static" / "object_store_data"
    INVOICES_DIR = BASE_THUMBS_DIR / "invoices"

    @override_settings(OBJECT_STORAGE_URL=BASE_THUMBS_DIR)
    def test_basics(self, clear_tests_invoices_bucket, invoice_data):
        existing_number_of_files = len(recursive_listdir(self.INVOICES_DIR))
        business_unit, stocks = invoice_data
        bookings = []
        for stock in stocks:
            booking = bookings_factories.UsedBookingFactory(stock=stock)
            bookings.append(booking)
        for booking in bookings[:3]:
            api.price_booking(booking)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        for booking in bookings[3:]:
            api.price_booking(booking)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        cashflows = (
            models.Cashflow.query.join(models.Cashflow.pricings)
            .filter(models.Pricing.businessUnitId == business_unit.id)
            .all()
        )
        cashflow_ids = [c.id for c in cashflows]
        invoice = api._generate_invoice(business_unit_id=business_unit.id, cashflow_ids=cashflow_ids)

        invoice_html = api._generate_invoice_html(invoice)
        api._store_invoice_pdf(invoice.storage_object_id, invoice_html)

        assert invoice.url == f"{self.INVOICES_DIR}/{invoice.storage_object_id}"
        assert len(recursive_listdir(self.INVOICES_DIR)) == existing_number_of_files + 2
        assert (self.INVOICES_DIR / f"{invoice.storage_object_id}").exists()
        assert (self.INVOICES_DIR / f"{invoice.storage_object_id}.type").exists()


class GenerateAndStoreInvoiceTest:
    BASE_THUMBS_DIR = pathlib.Path(tests.__path__[0]) / ".." / "src" / "pcapi" / "static" / "object_store_data"

    @override_settings(OBJECT_STORAGE_URL=BASE_THUMBS_DIR)
    def test_basics(self, clear_tests_invoices_bucket, invoice_data):
        business_unit, stocks = invoice_data
        bookings = []
        for stock in stocks:
            booking = bookings_factories.UsedBookingFactory(stock=stock)
            bookings.append(booking)
        for booking in bookings[:3]:
            api.price_booking(booking)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        for booking in bookings[3:]:
            api.price_booking(booking)
        api.generate_cashflows(cutoff=datetime.datetime.utcnow())
        cashflows = (
            models.Cashflow.query.join(models.Cashflow.pricings)
            .filter(models.Pricing.businessUnitId == business_unit.id)
            .all()
        )
        cashflow_ids = [c.id for c in cashflows]

        api.generate_and_store_invoice(business_unit_id=business_unit.id, cashflow_ids=cashflow_ids)  # does not raise

        assert len(mails_testing.outbox) == 1  # test number of emails sent


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
    factories.CashflowPricingFactory(cashflow=cf_3_2)
    cf_4_2 = factories.CashflowFactory(batch=batch4, businessUnit=bu2, amount=640)
    factories.CashflowPricingFactory(cashflow=cf_4_2)
    # Business unit 3: batches 3 and 5.
    cf_3_3 = factories.CashflowFactory(batch=batch3, businessUnit=bu3, amount=1280)
    factories.CashflowPricingFactory(cashflow=cf_3_3)
    cf_5_3 = factories.CashflowFactory(batch=batch5, businessUnit=bu3, amount=2560)
    factories.CashflowPricingFactory(cashflow=cf_5_3)
    # Business unit 4: batch 3 only
    cf_3_4 = factories.CashflowFactory(batch=batch3, businessUnit=bu4, amount=5120)
    factories.CashflowPricingFactory(cashflow=cf_3_4)
    # Business unit 5: batch 5 (nothing to do)
    cf_5_5 = factories.CashflowFactory(batch=batch5, businessUnit=bu5, amount=10240)
    factories.CashflowPricingFactory(cashflow=cf_5_5)

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
