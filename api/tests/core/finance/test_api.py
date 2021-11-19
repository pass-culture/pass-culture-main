import csv
import datetime
import io
from unittest import mock
import zipfile

import pytest
import sqlalchemy.orm as sqla_orm

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.bookings.models as bookings_models
from pcapi.core.categories import subcategories
from pcapi.core.finance import api
from pcapi.core.finance import exceptions
from pcapi.core.finance import factories
from pcapi.core.finance import models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import clean_temporary_files
import pcapi.core.users.factories as users_factories
from pcapi.utils import human_ids


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

    def test_price_booking_checks_business_unit(self):
        booking = bookings_factories.UsedBookingFactory(stock__offer__venue__businessUnit__siret=None)
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


class GenerateCashflowsTest:
    def test_basics(self):
        business_unit1 = factories.BusinessUnitFactory()
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
            amount=-3000,
        )
        pricing_no_bank_account = factories.PricingFactory(booking__stock__offer__venue__businessUnit__bankAccount=None)
        pricing_pending = factories.PricingFactory(status=models.PricingStatus.PENDING)
        cutoff = datetime.datetime.utcnow()
        pricing_after_cutoff = factories.PricingFactory()

        batch_id = api.generate_cashflows(cutoff)

        batch = models.CashflowBatch.query.one()
        assert batch.id == batch_id
        assert batch.cutoff == cutoff
        assert models.Cashflow.query.count() == 2
        assert len(pricing11.cashflows) == 1
        assert len(pricing12.cashflows) == 1
        assert pricing11.cashflows[0] == pricing12.cashflows[0]
        assert pricing11.cashflows[0].amount == -2000
        assert pricing11.cashflows[0].bankAccount == business_unit1.bankAccount
        assert pricing2.cashflows[0].amount == -3000

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
        name="Venue 1 only name",
        publicName=None,
        siret="siret 1",
        businessUnit__name="Business unit 1",
        businessUnit__bankAccount__bic="bic 1",
        businessUnit__bankAccount__iban="iban 1",
    )
    business_unit1 = venue1.businessUnit
    offers_factories.VenueFactory(businessUnit=business_unit1)
    venue2 = offers_factories.VenueFactory(
        name="dummy, we should use publicName instead",
        siret="siret 2",
        publicName="Venue 2 public name",
        businessUnit__name="Business unit 2",
        businessUnit__bankAccount__bic="bic 2",
        businessUnit__bankAccount__iban="iban 2",
    )

    n_queries = 1  # select business unit data
    with assert_num_queries(n_queries):
        path = api._generate_business_units_file()

    reader = csv.DictReader(path.open(), quoting=csv.QUOTE_NONNUMERIC)
    rows = list(reader)
    assert len(rows) == 2
    assert rows[0] == {
        "Identifiant de la BU": human_ids.humanize(venue1.id),
        "SIRET": "siret 1",
        "Raison sociale de la BU": "Business unit 1",
        "Libellé de la BU": "Venue 1 only name",
        "IBAN": "iban 1",
        "BIC": "bic 1",
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
        name="Le Petit Rintintin",
        siret="11111111122222",
    )
    pricing1 = factories.PricingFactory(
        amount=-1000,  # rate = 100 %
        booking__amount=10,
        booking__dateUsed=used_date,
        booking__stock__offer__name="Une histoire formidable",
        booking__stock__offer__subcategoryId=subcategories.SUPPORT_PHYSIQUE_FILM.id,
        booking__stock__offer__venue=venue1,
    )
    # These other pricings belong to a business unit whose venue is
    # NOT the venue of the offers.
    business_unit_venue2 = offers_factories.VenueFactory(
        siret="22222222233333",
        name="BU du Gigantesque Cubitus",
    )
    business_unit2 = business_unit_venue2.businessUnit
    offer_venue2 = offers_factories.VenueFactory(
        name="Le Gigantesque Cubitus",
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
    assert len(rows) == 3
    assert rows[0] == {
        "Identifiant de la BU": human_ids.humanize(venue1.id),
        "SIRET de la BU": "11111111122222",
        "Libellé de la BU": "Le Petit Rintintin",
        "Identifiant du lieu": human_ids.humanize(venue1.id),
        "Libellé du lieu": "Le Petit Rintintin",
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

    reader = csv.DictReader(path.open(), quoting=csv.QUOTE_NONNUMERIC)
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
