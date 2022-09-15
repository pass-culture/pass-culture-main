import datetime
import decimal

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
from pcapi.core.finance import api
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.finance import repository
from pcapi.core.finance.models import BankInformationStatus
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offerers.models as offerers_models
import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.core.testing import override_features
import pcapi.core.users.factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class GetBusinessUnitsTest:
    def test_basics(self):
        admin = users_factories.AdminFactory()
        venue = offerers_factories.VenueFactory()
        business_unit1 = venue.businessUnit
        offerers_factories.VenueFactory(businessUnit=business_unit1)
        other_venue = offerers_factories.VenueFactory()
        business_unit2 = other_venue.businessUnit

        business_units = repository.get_business_units_query(admin)
        business_units = list(business_units.order_by(models.BusinessUnit.id))
        assert business_units == [business_unit1, business_unit2]

    def test_pro(self):
        venue = offerers_factories.VenueFactory()
        business_unit1 = venue.businessUnit
        offerers_factories.VenueFactory(businessUnit=business_unit1)
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=venue.managingOfferer)
        _other_venue_with_business_unit = offerers_factories.VenueFactory()

        business_unit2 = factories.BusinessUnitFactory()
        factories.InvoiceFactory(businessUnit=business_unit2, amount=-15000000)
        venue2 = offerers_factories.VenueFactory(businessUnit=business_unit2)
        offerer2 = venue2.managingOfferer

        offerers_factories.UserOffererFactory(user=pro, offerer=offerer2, validationToken="token")
        business_units = list(repository.get_business_units_query(pro))
        assert business_units == [business_unit1]

    def test_admin_and_filter_on_offerer_id(self):
        admin = users_factories.AdminFactory()
        venue1 = offerers_factories.VenueFactory()
        business_unit1 = venue1.businessUnit
        offerers_factories.VenueFactory(businessUnit=business_unit1)
        offerer_id = venue1.managingOffererId
        _other_venue_with_business_unit = offerers_factories.VenueFactory()

        business_units = repository.get_business_units_query(admin, offerer_id=offerer_id)
        business_units = list(business_units.order_by(models.BusinessUnit.id))
        assert business_units == [business_unit1]

    def test_pro_and_filter_on_offerer_id(self):
        venue = offerers_factories.VenueFactory()
        offerer_id = venue.managingOffererId
        business_unit1 = venue.businessUnit
        offerers_factories.VenueFactory(businessUnit=business_unit1)
        other_venue = offerers_factories.VenueFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=venue.managingOfferer)
        offerers_factories.UserOffererFactory(user=pro, offerer=other_venue.managingOfferer)
        business_units = list(repository.get_business_units_query(pro, offerer_id=offerer_id))
        assert business_units == [business_unit1]

    def test_check_offerer_id_and_pro_user(self):
        # Make sure that a pro user cannot specify an offerer id for
        # which they don't have access.
        venue = offerers_factories.VenueFactory()
        offerer_id = venue.managingOffererId
        pro = users_factories.ProFactory()

        business_units = repository.get_business_units_query(pro, offerer_id=offerer_id)
        assert not business_units.count()

    def test_return_accepted_bank_information_only(self):
        admin = users_factories.AdminFactory()
        venue = offerers_factories.VenueFactory()
        business_unit1 = venue.businessUnit
        offerers_factories.VenueFactory(businessUnit=business_unit1)
        _other_venue = offerers_factories.VenueFactory(
            businessUnit__bankAccount__status=models.BankInformationStatus.REJECTED,
        )

        business_units = repository.get_business_units_query(admin)
        business_units = list(business_units.order_by(models.BusinessUnit.id))
        assert business_units == [business_unit1]


class GetReimbursementPointsTest:
    def test_admin(self):
        admin = users_factories.AdminFactory()
        reimbursement_point1 = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(venue=reimbursement_point1)
        reimbursement_point2 = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(venue=reimbursement_point2)

        reimbursement_points = repository.get_reimbursement_points_query(admin)
        reimbursement_points = list(reimbursement_points.order_by(offerers_models.Venue.id))

        assert reimbursement_points == [reimbursement_point1, reimbursement_point2]

    def test_pro(self):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        reimbursement_point1 = offerers_factories.VenueFactory(managingOfferer=offerer, reimbursement_point="self")
        factories.BankInformationFactory(venue=reimbursement_point1)
        reimbursement_point2 = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(venue=reimbursement_point2)

        reimbursement_points = list(repository.get_reimbursement_points_query(pro))

        assert reimbursement_points == [reimbursement_point1]

    def test_admin_and_filter_on_offerer_id(self):
        admin = users_factories.AdminFactory()
        offerer1 = offerers_factories.OffererFactory()
        reimbursement_point1 = offerers_factories.VenueFactory(managingOfferer=offerer1, reimbursement_point="self")
        factories.BankInformationFactory(venue=reimbursement_point1)
        reimbursement_point2 = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(venue=reimbursement_point2)

        reimbursement_points = repository.get_reimbursement_points_query(user=admin, offerer_id=offerer1.id)
        reimbursement_points = list(reimbursement_points.order_by(offerers_models.Venue.id))

        assert reimbursement_points == [reimbursement_point1]

    def test_pro_and_filter_on_offerer_id(self):
        offerer1 = offerers_factories.OffererFactory()
        reimbursement_point1 = offerers_factories.VenueFactory(managingOfferer=offerer1, reimbursement_point="self")
        factories.BankInformationFactory(venue=reimbursement_point1)
        offerer2 = offerers_factories.OffererFactory()
        reimbursement_point2 = offerers_factories.VenueFactory(managingOfferer=offerer2, reimbursement_point="self")
        factories.BankInformationFactory(venue=reimbursement_point2)
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer1)

        reimbursement_points = list(repository.get_reimbursement_points_query(pro, offerer_id=offerer1.id))

        assert reimbursement_points == [reimbursement_point1]

    def test_check_offerer_id_and_pro_user(self):
        # Make sure that a pro user cannot specify an offerer id for
        # which they don't have access.
        offerer1 = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer1)
        reimbursement_point1 = offerers_factories.VenueFactory(managingOfferer=offerer1, reimbursement_point="self")
        factories.BankInformationFactory(venue=reimbursement_point1)
        offerer2 = offerers_factories.OffererFactory()
        reimbursement_point2 = offerers_factories.VenueFactory(managingOfferer=offerer2, reimbursement_point="self")
        factories.BankInformationFactory(venue=reimbursement_point2)

        reimbursement_points = repository.get_reimbursement_points_query(pro, offerer_id=offerer2.id)

        assert reimbursement_points.count() == 0

    def test_return_accepted_bank_information_only(self):
        admin = users_factories.AdminFactory()
        reimbursement_point1 = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(venue=reimbursement_point1)
        reimbursement_point2 = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.BankInformationFactory(venue=reimbursement_point2, status=BankInformationStatus.DRAFT)

        reimbursement_points = repository.get_reimbursement_points_query(admin)
        reimbursement_points = list(reimbursement_points.order_by(offerers_models.Venue.id))

        assert reimbursement_points == [reimbursement_point1]


class GetInvoicesQueryTest:
    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=True)
    def test_basics(self):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        reimbursement_point1 = offerers_factories.VenueFactory(managingOfferer=offerer, reimbursement_point="self")
        invoice1 = factories.InvoiceFactory(businessUnit=None, reimbursementPoint=reimbursement_point1)
        reimbursement_point2 = offerers_factories.VenueFactory(managingOfferer=offerer, reimbursement_point="self")
        invoice2 = factories.InvoiceFactory(businessUnit=None, reimbursementPoint=reimbursement_point2)
        _other_reimbursement_point = offerers_factories.VenueFactory(reimbursement_point="self")
        _other_invoice = factories.InvoiceFactory(businessUnit=None, reimbursementPoint=_other_reimbursement_point)

        reimbursement_point3 = offerers_factories.VenueFactory(reimbursement_point="self")
        factories.InvoiceFactory(businessUnit=None, reimbursementPoint=reimbursement_point3, amount=-15000000)
        offerer2 = reimbursement_point3.managingOfferer
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer2, validationToken="token")

        invoices = repository.get_invoices_query(pro).order_by(models.Invoice.id)
        assert list(invoices) == [invoice1, invoice2]

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=True)
    def test_filter_on_date(self):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        reimbursement_point = offerers_factories.VenueFactory(managingOfferer=offerer, reimbursement_point="self")
        _invoice_before = factories.InvoiceFactory(
            businessUnit=None,
            reimbursementPoint=reimbursement_point,
            date=datetime.date(2021, 6, 15),
        )
        invoice_within = factories.InvoiceFactory(
            businessUnit=None,
            reimbursementPoint=reimbursement_point,
            date=datetime.date(2021, 7, 1),
        )
        _invoice_after = factories.InvoiceFactory(
            businessUnit=None,
            reimbursementPoint=reimbursement_point,
            date=datetime.date(2021, 8, 1),
        )

        invoices = repository.get_invoices_query(
            pro,
            date_from=datetime.date(2021, 7, 1),
            date_until=datetime.date(2021, 8, 1),
        )
        assert list(invoices) == [invoice_within]

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=True)
    def test_filter_on_reimbursement_point(self):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        reimbursement_point1 = offerers_factories.VenueFactory(managingOfferer=offerer, reimbursement_point="self")
        invoice1 = factories.InvoiceFactory(businessUnit=None, reimbursementPoint=reimbursement_point1)
        reimbursement_point2 = offerers_factories.VenueFactory(managingOfferer=offerer, reimbursement_point="self")
        _invoice2 = factories.InvoiceFactory(businessUnit=None, reimbursementPoint=reimbursement_point2)

        invoices = repository.get_invoices_query(
            pro,
            reimbursement_point_id=reimbursement_point1.id,
        )
        assert list(invoices) == [invoice1]

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=True)
    def test_wrong_reimbursement_point(self):
        # Make sure that specifying a reimbursement point id that belongs to
        # another offerer does not return anything.
        offerer = offerers_factories.OffererFactory()
        pro1 = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro1, offerer=offerer)
        reimbursement_point = offerers_factories.VenueFactory(managingOfferer=offerer, reimbursement_point="self")
        _invoice1 = factories.InvoiceFactory(businessUnit=None, reimbursementPoint=reimbursement_point)

        other_reimbursement_point = offerers_factories.VenueFactory(reimbursement_point="self")
        _invoice2 = factories.InvoiceFactory(businessUnit=None, reimbursementPoint=other_reimbursement_point)

        invoices = repository.get_invoices_query(
            pro1,
            reimbursement_point_id=other_reimbursement_point.id,
        )
        assert invoices.count() == 0

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=True)
    def test_admin_filter_on_reimbursement_point(self):
        reimbursement_point1 = offerers_factories.VenueFactory(reimbursement_point="self")
        invoice1 = factories.InvoiceFactory(businessUnit=None, reimbursementPoint=reimbursement_point1)
        reimbursement_point2 = offerers_factories.VenueFactory(reimbursement_point="self")
        _invoice2 = factories.InvoiceFactory(businessUnit=None, reimbursementPoint=reimbursement_point2)

        admin = users_factories.AdminFactory()

        invoices = repository.get_invoices_query(
            admin,
            reimbursement_point_id=reimbursement_point1.id,
        )
        assert list(invoices) == [invoice1]

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=True)
    def test_admin_without_filter(self):
        factories.InvoiceFactory(
            businessUnit=None,
        )
        admin = users_factories.AdminFactory()

        invoices = repository.get_invoices_query(admin)
        assert invoices.count() == 0


class LegacyGetInvoicesQueryTest:
    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=False)
    def test_basics(self):
        business_unit1 = factories.BusinessUnitFactory()
        invoice1 = factories.InvoiceFactory(businessUnit=business_unit1, reimbursementPoint=None)
        business_unit2 = factories.BusinessUnitFactory()
        invoice2 = factories.InvoiceFactory(businessUnit=business_unit2, reimbursementPoint=None)
        venue1 = offerers_factories.VenueFactory(businessUnit=business_unit1)
        offerer = venue1.managingOfferer
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        _venue2 = offerers_factories.VenueFactory(
            managingOfferer=offerer,
            businessUnit=business_unit2,
        )
        other_business_unit = factories.BusinessUnitFactory()
        _other_venue = offerers_factories.VenueFactory(businessUnit=other_business_unit)
        _other_invoice = factories.InvoiceFactory(businessUnit=other_business_unit)

        business_unit3 = factories.BusinessUnitFactory()
        factories.InvoiceFactory(businessUnit=business_unit3, amount=-15000000)
        venue3 = offerers_factories.VenueFactory(businessUnit=business_unit3)
        offerer2 = venue3.managingOfferer
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer2, validationToken="token")

        invoices = repository.get_invoices_query(pro).order_by(models.Invoice.id)
        assert list(invoices) == [invoice1, invoice2]

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=False)
    def test_filter_on_date(self):
        business_unit = factories.BusinessUnitFactory()
        venue = offerers_factories.VenueFactory(businessUnit=business_unit)
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=venue.managingOfferer)
        _invoice_before = factories.InvoiceFactory(
            businessUnit=business_unit,
            date=datetime.date(2021, 6, 15),
        )
        invoice_within = factories.InvoiceFactory(
            businessUnit=business_unit,
            date=datetime.date(2021, 7, 1),
        )
        _invoice_after = factories.InvoiceFactory(
            businessUnit=business_unit,
            date=datetime.date(2021, 8, 1),
        )

        invoices = repository.get_invoices_query(
            pro,
            date_from=datetime.date(2021, 7, 1),
            date_until=datetime.date(2021, 8, 1),
        )
        assert list(invoices) == [invoice_within]

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=False)
    def test_filter_on_business_unit(self):
        business_unit1 = factories.BusinessUnitFactory()
        invoice1 = factories.InvoiceFactory(businessUnit=business_unit1)
        venue1 = offerers_factories.VenueFactory(businessUnit=business_unit1)
        pro1 = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro1, offerer=venue1.managingOfferer)
        business_unit2 = factories.BusinessUnitFactory()
        _invoice2 = factories.InvoiceFactory(businessUnit=business_unit2)

        invoices = repository.get_invoices_query(
            pro1,
            business_unit_id=business_unit1.id,
        )
        assert list(invoices) == [invoice1]

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=False)
    def test_wrong_business_unit(self):
        # Make sure that specifying a business unit id that belongs to
        # another offerer does not return anything.
        business_unit1 = factories.BusinessUnitFactory()
        _invoice1 = factories.InvoiceFactory(businessUnit=business_unit1)
        venue1 = offerers_factories.VenueFactory(businessUnit=business_unit1)
        pro1 = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro1, offerer=venue1.managingOfferer)

        other_business_unit = factories.BusinessUnitFactory()
        _other_venue = offerers_factories.VenueFactory(businessUnit=other_business_unit)
        _other_invoice = factories.InvoiceFactory(businessUnit=other_business_unit)

        invoices = repository.get_invoices_query(
            pro1,
            business_unit_id=other_business_unit.id,
        )
        assert not invoices.count()

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=False)
    def test_admin_filter_on_business_unit(self):
        invoice1 = factories.InvoiceFactory()
        _venue1 = offerers_factories.VenueFactory(businessUnit=invoice1.businessUnit)
        invoice2 = factories.InvoiceFactory()
        _venue2 = offerers_factories.VenueFactory(businessUnit=invoice2.businessUnit)
        admin = users_factories.AdminFactory()

        invoices = repository.get_invoices_query(
            admin,
            business_unit_id=invoice1.businessUnitId,
        )
        assert list(invoices) == [invoice1]

    @override_features(ENABLE_NEW_BANK_INFORMATIONS_CREATION=False)
    def test_admin_without_filter(self):
        invoice = factories.InvoiceFactory()
        _venue = offerers_factories.VenueFactory(businessUnit=invoice.businessUnit)
        admin = users_factories.AdminFactory()

        invoices = repository.get_invoices_query(admin)
        assert not invoices.count()


def test_has_reimbursement():
    booking = bookings_factories.UsedIndividualBookingFactory()
    assert not repository.has_reimbursement(booking)

    pricing = factories.PricingFactory(booking=booking, status=models.PricingStatus.VALIDATED)
    assert not repository.has_reimbursement(booking)

    pricing.status = models.PricingStatus.PROCESSED
    db.session.add(pricing)
    db.session.commit()
    assert repository.has_reimbursement(booking)


class HasActiveOrFutureCustomRemibursementRuleTest:
    def test_active_rule(self):
        now = datetime.datetime.utcnow()
        timespan = (now - datetime.timedelta(days=1), now + datetime.timedelta(days=1))
        rule = payments_factories.CustomReimbursementRuleFactory(timespan=timespan)
        offer = rule.offer
        assert repository.has_active_or_future_custom_reimbursement_rule(offer)

    def test_future_rule(self):
        now = datetime.datetime.utcnow()
        timespan = (now + datetime.timedelta(days=1), None)
        rule = payments_factories.CustomReimbursementRuleFactory(timespan=timespan)
        offer = rule.offer
        assert repository.has_active_or_future_custom_reimbursement_rule(offer)

    def test_past_rule(self):
        now = datetime.datetime.utcnow()
        timespan = (now - datetime.timedelta(days=2), now - datetime.timedelta(days=1))
        rule = payments_factories.CustomReimbursementRuleFactory(timespan=timespan)
        offer = rule.offer
        assert not repository.has_active_or_future_custom_reimbursement_rule(offer)


@pytest.mark.usefixtures("db_session")
class FindAllOffererPaymentsTest:
    def test_should_not_return_payment_info_with_error_status(self):
        # Given
        payment = factories.PaymentFactory()
        offerer = payment.booking.offerer
        factories.PaymentStatusFactory(
            payment=payment,
            status=models.TransactionStatus.ERROR,
            detail="Iban non fourni",
        )

        # When
        reimbursement_period = (datetime.date.today(), datetime.date.today() + datetime.timedelta(days=2))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 0

    def test_should_return_one_payment_info_with_sent_status(self):
        # Given
        payment = factories.PaymentFactory()
        for status in (
            models.TransactionStatus.ERROR,
            models.TransactionStatus.RETRY,
            models.TransactionStatus.SENT,
        ):
            factories.PaymentStatusFactory(payment=payment, status=status)
        offerer = payment.booking.offerer

        # When
        reimbursement_period = (datetime.date.today(), datetime.date.today() + datetime.timedelta(days=2))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 1
        # No need to test the contents of `payments[0]`, it's already
        # done in `test_with_new_models()` below.

    def test_should_return_one_payment_info_with_sent_status_when_offer_educational(self):
        # Given
        collective_booking = UsedCollectiveBookingFactory(
            educationalRedactor__firstName="Dominique",
            educationalRedactor__lastName="Leprof",
        )
        offerer = collective_booking.offerer
        payment = factories.PaymentFactory(collectiveBooking=collective_booking)
        factories.PaymentStatusFactory(
            payment=payment,
            status=models.TransactionStatus.SENT,
        )

        # When
        reimbursement_period = (datetime.date.today(), datetime.date.today() + datetime.timedelta(days=2))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 1
        assert payments[0].collective_booking_id is not None
        assert payments[0].redactor_firstname == "Dominique"
        assert payments[0].redactor_lastname == "Leprof"
        # The rest is tested in `test_with_new_models()` below.

    def test_should_return_last_matching_status_based_on_date_for_each_payment(self):
        # Given
        stock = offers_factories.ThingStockFactory()
        offerer = stock.offer.venue.managingOfferer
        booking1 = bookings_factories.UsedIndividualBookingFactory(
            stock=stock,
            token="TOKEN1",
        )
        booking2 = bookings_factories.UsedIndividualBookingFactory(
            stock=stock,
            token="TOKEN2",
        )

        payment1 = factories.PaymentFactory(booking=booking1)
        factories.PaymentStatusFactory(
            payment=payment1,
            status=models.TransactionStatus.RETRY,
        )
        factories.PaymentStatusFactory(
            payment=payment1,
            status=models.TransactionStatus.SENT,
        )

        payment2 = factories.PaymentFactory(booking=booking2)
        factories.PaymentStatusFactory(
            payment=payment2,
            status=models.TransactionStatus.ERROR,
        )
        factories.PaymentStatusFactory(
            payment=payment2,
            status=models.TransactionStatus.SENT,
        )

        # When
        reimbursement_period = (datetime.date.today(), datetime.date.today() + datetime.timedelta(days=2))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 2
        assert payments[0].booking_token == "TOKEN2"
        assert payments[1].booking_token == "TOKEN1"

    def test_should_return_payments_from_multiple_venues(self):
        # Given
        offerer = offerers_factories.OffererFactory()
        factories.PaymentStatusFactory(
            payment__booking__stock__offer__venue__managingOfferer=offerer, status=models.TransactionStatus.SENT
        )
        factories.PaymentStatusFactory(
            payment__booking__stock__offer__venue__managingOfferer=offerer, status=models.TransactionStatus.SENT
        )

        # When
        reimbursement_period = (datetime.date.today(), datetime.date.today() + datetime.timedelta(days=2))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 2

    def test_should_return_payments_filtered_by_venue(self):
        # Given
        offerer = offerers_factories.OffererFactory()
        venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer)
        venue_2 = offerers_factories.VenueFactory(managingOfferer=offerer)

        payment_1 = factories.PaymentFactory(booking__stock__offer__venue=venue_1)
        factories.PaymentStatusFactory(payment=payment_1, status=models.TransactionStatus.SENT)
        payment_2 = factories.PaymentFactory(booking__stock__offer__venue=venue_2)
        factories.PaymentStatusFactory(payment=payment_2, status=models.TransactionStatus.SENT)

        # When
        reimbursement_period = (datetime.date.today(), datetime.date.today() + datetime.timedelta(days=2))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period, venue_1.id)

        # Then
        assert len(payments) == 1
        assert payment_1.booking.token in payments[0]
        assert venue_1.name in payments[0]

    def test_should_return_payments_filtered_by_payment_date(self):
        # Given
        tomorrow_at_nine = datetime.datetime.combine(
            datetime.date.today() + datetime.timedelta(days=1), datetime.datetime.min.time()
        ) + datetime.timedelta(hours=9)
        offerer = offerers_factories.OffererFactory()
        venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer)
        payment_1 = factories.PaymentFactory(booking__stock__offer__venue=venue_1)
        factories.PaymentStatusFactory(date=tomorrow_at_nine, payment=payment_1, status=models.TransactionStatus.SENT)
        payment_2 = factories.PaymentFactory(booking__stock__offer__venue=venue_1)
        factories.PaymentStatusFactory(
            date=datetime.date.today() + datetime.timedelta(days=2),
            payment=payment_2,
            status=models.TransactionStatus.SENT,
        )

        # When
        reimbursement_period = (datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 1
        assert payment_1.booking.token in payments[0]
        assert venue_1.name in payments[0]

    # FIXME (dbaty, 2022-03-15): once we have Pricing and Cashflow for
    # pre-2022 payments, we can rename and update this test. Some
    # tests above could be updated, some could be removed if they
    # don't make sense.
    @override_features(USE_REIMBURSEMENT_POINT_FOR_CASHFLOWS=True)
    def test_with_new_models(self):
        stock = offers_factories.ThingStockFactory(
            offer__name="Test Book",
            offer__venue__managingOfferer__address="7 rue du livre",
            offer__venue__name="La petite librairie",
            offer__venue__address="123 rue de Paris",
            offer__venue__postalCode="75000",
            offer__venue__city="Paris",
            offer__venue__siret=12345678912345,
            offer__venue__reimbursement_point="self",
            price=10,
        )
        # FIXME (dbaty, 2022-09-14): the BankInformation object should
        # automatically be created by the Venue factory when linking a
        # reimbursement point.
        factories.BankInformationFactory(venue=stock.offer.venue, iban="CF13QSDFGH456789")
        booking = bookings_factories.UsedIndividualBookingFactory(
            stock=stock,
            token="ABCDEF",
        )

        # Create an old-style payment
        payment = factories.PaymentFactory(
            amount=9.5,
            reimbursementRate=0.95,
            booking=booking,
            iban="CF13QSDFGH456789",
            transactionLabel="pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        )
        factories.PaymentStatusFactory(
            payment=payment,
            status=models.TransactionStatus.SENT,
        )

        # Create a new-style pricing on the same booking. In real life
        # we cannot have a booking linked to both sets of models, but
        # here it's useful because we can test that the data is the
        # same.
        factories.PricingFactory(
            booking=booking,
            amount=-9500,
            standardRule="Remboursement à 95% au dessus de 20 000 € pour les livres",
            status=models.PricingStatus.VALIDATED,
        )
        api.generate_cashflows_and_payment_files(datetime.datetime.utcnow())
        api.generate_invoices()
        cashflow = models.Cashflow.query.one()
        invoice = models.Invoice.query.one()

        reimbursement_period = (datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1))
        payments = repository.find_all_offerer_payments(booking.offerer.id, reimbursement_period)

        expected_in_both = {
            "booking_token": "ABCDEF",
            "booking_used_date": booking.dateUsed,
            "booking_quantity": 1,
            "booking_amount": decimal.Decimal("10.00"),
            "offer_name": "Test Book",
            "collective_booking_id": None,
            "venue_name": "La petite librairie",
            "venue_address": "123 rue de Paris",
            "venue_postal_code": "75000",
            "venue_city": "Paris",
            "venue_siret": "12345678912345",
            "iban": "CF13QSDFGH456789",
        }
        specific_for_payment = {
            "amount": decimal.Decimal("9.50"),
            "reimbursement_rate": decimal.Decimal("0.95"),
            "transaction_label": "pass Culture Pro - remboursement 1ère quinzaine 07-2019",
        }
        specific_for_pricing = {
            "amount": decimal.Decimal("9500"),
            "rule_name": "Remboursement à 95% au dessus de 20 000 € pour les livres",
            "rule_id": None,
            "reimbursement_point_name": "La petite librairie",
            "reimbursement_point_address": "123 rue de Paris",
            "reimbursement_point_postal_code": "75000",
            "reimbursement_point_city": "Paris",
            "reimbursement_point_siret": "12345678912345",
            "cashflow_batch_cutoff": cashflow.batch.cutoff,
            "cashflow_batch_label": cashflow.batch.label,
            "invoice_date": invoice.date,
            "invoice_reference": invoice.reference,
        }

        missing_for_payment = (set(expected_in_both.keys()) | set(specific_for_payment.keys())).symmetric_difference(
            set(payments[1]._asdict())
        )
        assert missing_for_payment == set()
        for attr, expected in expected_in_both.items():
            assert getattr(payments[1], attr) == expected, f"wrong {attr}"
        for attr, expected in specific_for_payment.items():
            assert getattr(payments[1], attr) == expected, f"wrong {attr}"

        missing_for_pricing = (set(expected_in_both.keys()) | set(specific_for_pricing.keys())).symmetric_difference(
            set(payments[0]._asdict())
        )
        assert missing_for_pricing == set()
        for attr, expected in expected_in_both.items():
            assert getattr(payments[0], attr) == expected, f"wrong {attr}"
        for attr, expected in specific_for_pricing.items():
            assert getattr(payments[0], attr) == expected, f"wrong {attr}"
