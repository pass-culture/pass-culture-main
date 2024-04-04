import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.finance import repository
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
import pcapi.core.users.factories as users_factories
from pcapi.models import db


pytestmark = pytest.mark.usefixtures("db_session")


class GetInvoicesQueryTest:
    def test_basics(self):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account1 = factories.BankAccountFactory(offerer=offerer)
        invoice1 = factories.InvoiceFactory(bankAccount=bank_account1)
        bank_account2 = factories.BankAccountFactory(offerer=offerer)
        invoice2 = factories.InvoiceFactory(bankAccount=bank_account2)
        other_bank_account = factories.BankAccountFactory()
        _other_invoice = factories.InvoiceFactory(bankAccount=other_bank_account)

        bank_account3 = factories.BankAccountFactory()
        factories.InvoiceFactory(bankAccount=bank_account3, amount=-15000000)
        offerer2 = bank_account3.offerer
        offerers_factories.NotValidatedUserOffererFactory(user=pro, offerer=offerer2)

        invoices = repository.get_invoices_query(pro).order_by(models.Invoice.id)
        assert list(invoices) == [invoice1, invoice2]

    def test_filter_on_date(self):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account = factories.BankAccountFactory(offerer=offerer)
        _invoice_before = factories.InvoiceFactory(
            bankAccount=bank_account,
            date=datetime.date(2021, 6, 15),
        )
        invoice_within = factories.InvoiceFactory(
            bankAccount=bank_account,
            date=datetime.date(2021, 7, 1),
        )
        _invoice_after = factories.InvoiceFactory(
            bankAccount=bank_account,
            date=datetime.date(2021, 8, 1),
        )

        invoices = repository.get_invoices_query(
            pro,
            date_from=datetime.date(2021, 7, 1),
            date_until=datetime.date(2021, 8, 1),
        )
        assert list(invoices) == [invoice_within]

    def test_filter_on_bank_account(self):
        offerer = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer)
        bank_account1 = factories.BankAccountFactory(offerer=offerer)
        invoice1 = factories.InvoiceFactory(bankAccount=bank_account1)
        bank_account2 = factories.BankAccountFactory(offerer=offerer)
        _invoice2 = factories.InvoiceFactory(bankAccount=bank_account2)

        invoices = repository.get_invoices_query(
            pro,
            bank_account_id=bank_account1.id,
        )
        assert list(invoices) == [invoice1]

    def test_wrong_bank_account(self):
        # Make sure that specifying a bank account id that belongs to
        # another offerer does not return anything.
        offerer = offerers_factories.OffererFactory()
        pro1 = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro1, offerer=offerer)
        bank_account = factories.BankAccountFactory(offerer=offerer)
        _invoice1 = factories.InvoiceFactory(bankAccount=bank_account)

        other_bank_account = factories.BankAccountFactory()
        _invoice2 = factories.InvoiceFactory(bankAccount=other_bank_account)

        invoices = repository.get_invoices_query(
            pro1,
            bank_account_id=other_bank_account.id,
        )
        assert invoices.count() == 0

    def test_admin_filter_on_bank_account(self):
        bank_account1 = factories.BankAccountFactory()
        invoice1 = factories.InvoiceFactory(bankAccount=bank_account1)
        bank_account2 = factories.BankAccountFactory()
        _invoice2 = factories.InvoiceFactory(bankAccount=bank_account2)

        admin = users_factories.AdminFactory()

        invoices = repository.get_invoices_query(
            admin,
            bank_account_id=bank_account1.id,
        )
        assert list(invoices) == [invoice1]

    def test_filter_on_offerer_id(self):
        offerer1 = offerers_factories.OffererFactory()
        offerer2 = offerers_factories.OffererFactory()
        pro = users_factories.ProFactory()
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer1)
        offerers_factories.UserOffererFactory(user=pro, offerer=offerer2)
        bank_account1 = factories.BankAccountFactory(offerer=offerer1)
        _invoice1 = factories.InvoiceFactory(bankAccount=bank_account1)
        bank_account2 = factories.BankAccountFactory(offerer=offerer2)
        invoice2 = factories.InvoiceFactory(bankAccount=bank_account2)

        invoices = repository.get_invoices_query(
            pro,
            offerer_id=offerer2.id,
        )
        assert list(invoices) == [invoice2]

    def test_admin_without_filter(self):
        factories.InvoiceFactory()
        admin = users_factories.AdminFactory()

        invoices = repository.get_invoices_query(admin)
        assert invoices.count() == 0

    def test_has_invoice(self):
        offerer = offerers_factories.OffererFactory()
        bank_account = factories.BankAccountFactory(offerer=offerer)
        factories.InvoiceFactory(bankAccount=bank_account)

        assert repository.has_invoice(offerer.id)

    def test_has_no_invoices(self):
        offerer = offerers_factories.OffererFactory()
        offerer_2 = offerers_factories.OffererFactory()
        bank_account = factories.BankAccountFactory(offerer=offerer_2)
        factories.InvoiceFactory(bankAccount=bank_account)

        assert not repository.has_invoice(offerer.id)


class HasReimbursementTest:
    def test_booking_status(self):
        confirmed = bookings_factories.BookingFactory()
        assert not repository.has_reimbursement(confirmed)

        used = bookings_factories.BookingFactory()
        assert not repository.has_reimbursement(used)

        cancelled = bookings_factories.BookingFactory()
        assert not repository.has_reimbursement(cancelled)

        reimbursed = bookings_factories.ReimbursedBookingFactory()
        assert repository.has_reimbursement(reimbursed)

    def test_pricing_status(self):
        booking = bookings_factories.UsedBookingFactory()
        assert not repository.has_reimbursement(booking)
        pricing = factories.PricingFactory(
            booking=booking,
            status=models.PricingStatus.VALIDATED,
        )
        assert not repository.has_reimbursement(booking)
        pricing.status = models.PricingStatus.PROCESSED
        db.session.flush()
        assert repository.has_reimbursement(booking)
        pricing.status = models.PricingStatus.INVOICED
        db.session.flush()
        assert repository.has_reimbursement(booking)


class HasActiveOrFutureCustomRemibursementRuleTest:
    def test_active_rule(self):
        now = datetime.datetime.utcnow()
        timespan = (now - datetime.timedelta(days=1), now + datetime.timedelta(days=1))
        rule = factories.CustomReimbursementRuleFactory(timespan=timespan)
        offer = rule.offer
        assert repository.has_active_or_future_custom_reimbursement_rule(offer)

    def test_future_rule(self):
        now = datetime.datetime.utcnow()
        timespan = (now + datetime.timedelta(days=1), None)
        rule = factories.CustomReimbursementRuleFactory(timespan=timespan)
        offer = rule.offer
        assert repository.has_active_or_future_custom_reimbursement_rule(offer)

    def test_past_rule(self):
        now = datetime.datetime.utcnow()
        timespan = (now - datetime.timedelta(days=2), now - datetime.timedelta(days=1))
        rule = factories.CustomReimbursementRuleFactory(timespan=timespan)
        offer = rule.offer
        assert not repository.has_active_or_future_custom_reimbursement_rule(offer)


@pytest.mark.usefixtures("db_session")
class FindAllOffererPaymentsTest:
    def test_should_not_return_payment_info_with_error_status(self):
        # Given
        payment = factories.PaymentFactory(booking__stock__offer__venue__pricing_point="self")
        offerer = payment.booking.offerer
        factories.PaymentStatusFactory(
            payment=payment,
            status=models.TransactionStatus.ERROR,
            detail="Iban non fourni",
            date=datetime.datetime(2021, 1, 1),
        )

        # When
        reimbursement_period = (datetime.date(2021, 1, 1), datetime.date(2021, 1, 15))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 0

    def test_should_return_one_payment_info_with_sent_status(self):
        # Given
        payment = factories.PaymentFactory(booking__stock__offer__venue__pricing_point="self")
        for status in (
            models.TransactionStatus.ERROR,
            models.TransactionStatus.RETRY,
            models.TransactionStatus.SENT,
        ):
            factories.PaymentStatusFactory(
                payment=payment,
                status=status,
                date=datetime.datetime(2021, 1, 1),
            )
        offerer = payment.booking.offerer

        # When
        reimbursement_period = (datetime.date(2021, 1, 1), datetime.date(2021, 1, 15))
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
        payment = factories.PaymentFactory(
            collectiveBooking=collective_booking, booking__stock__offer__venue__pricing_point="self"
        )
        factories.PaymentStatusFactory(
            payment=payment,
            status=models.TransactionStatus.SENT,
            date=datetime.datetime(2021, 1, 1),
        )

        # When
        reimbursement_period = (datetime.date(2021, 1, 1), datetime.date(2021, 1, 15))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 1
        assert payments[0].collective_booking_id is not None
        assert payments[0].redactor_firstname == "Dominique"
        assert payments[0].redactor_lastname == "Leprof"
        # The rest is tested in `test_with_new_models()` below.

    def test_should_return_last_matching_status_based_on_date_for_each_payment(self):
        # Given
        stock = offers_factories.ThingStockFactory(offer__venue__pricing_point="self")
        offerer = stock.offer.venue.managingOfferer
        booking1 = bookings_factories.UsedBookingFactory(
            stock=stock,
            token="TOKEN1",
        )
        booking2 = bookings_factories.UsedBookingFactory(
            stock=stock,
            token="TOKEN2",
        )

        payment1 = factories.PaymentFactory(booking=booking1)
        factories.PaymentStatusFactory(
            payment=payment1,
            status=models.TransactionStatus.RETRY,
            date=datetime.datetime(2021, 1, 1),
        )
        factories.PaymentStatusFactory(
            payment=payment1,
            status=models.TransactionStatus.SENT,
            date=datetime.datetime(2021, 1, 2),
        )

        payment2 = factories.PaymentFactory(booking=booking2)
        factories.PaymentStatusFactory(
            payment=payment2,
            status=models.TransactionStatus.ERROR,
            date=datetime.datetime(2021, 1, 3),
        )
        factories.PaymentStatusFactory(
            payment=payment2,
            status=models.TransactionStatus.SENT,
            date=datetime.datetime(2021, 1, 4),
        )

        # When
        reimbursement_period = (datetime.date(2021, 1, 1), datetime.date(2021, 1, 15))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 2
        assert payments[0].booking_token == "TOKEN2"
        assert payments[1].booking_token == "TOKEN1"

    def test_should_return_payments_from_multiple_venues(self):
        # Given
        offerer = offerers_factories.OffererFactory()
        factories.PaymentStatusFactory(
            payment__booking__stock__offer__venue__managingOfferer=offerer,
            payment__booking__stock__offer__venue__pricing_point="self",
            status=models.TransactionStatus.SENT,
            date=datetime.datetime(2021, 1, 1),
        )
        factories.PaymentStatusFactory(
            payment__booking__stock__offer__venue__managingOfferer=offerer,
            payment__booking__stock__offer__venue__pricing_point="self",
            status=models.TransactionStatus.SENT,
            date=datetime.datetime(2021, 1, 1),
        )

        # When
        reimbursement_period = (datetime.date(2021, 1, 1), datetime.date(2021, 1, 15))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 2

    def test_should_return_payments_filtered_by_venue(self):
        # Given
        offerer = offerers_factories.OffererFactory()
        venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
        venue_2 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")

        payment_1 = factories.PaymentFactory(booking__stock__offer__venue=venue_1)
        factories.PaymentStatusFactory(
            payment=payment_1,
            status=models.TransactionStatus.SENT,
            date=datetime.datetime(2021, 1, 1),
        )
        payment_2 = factories.PaymentFactory(booking__stock__offer__venue=venue_2)
        factories.PaymentStatusFactory(
            payment=payment_2,
            status=models.TransactionStatus.SENT,
            date=datetime.datetime(2021, 1, 1),
        )

        # When
        reimbursement_period = (datetime.date(2021, 1, 1), datetime.date(2021, 1, 15))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period, venue_1.id)

        # Then
        assert len(payments) == 1
        assert payment_1.booking.token in payments[0]
        assert venue_1.name in payments[0]

    def test_should_return_payments_filtered_by_payment_date(self):
        # Given
        offerer = offerers_factories.OffererFactory()
        venue_1 = offerers_factories.VenueFactory(managingOfferer=offerer, pricing_point="self")
        payment_1 = factories.PaymentFactory(booking__stock__offer__venue=venue_1)
        factories.PaymentStatusFactory(
            payment=payment_1,
            status=models.TransactionStatus.SENT,
            date=datetime.datetime(2021, 1, 1),
        )
        payment_2 = factories.PaymentFactory(booking__stock__offer__venue=venue_1)
        factories.PaymentStatusFactory(
            payment=payment_2,
            status=models.TransactionStatus.SENT,
            date=datetime.datetime(2021, 1, 16),
        )

        # When
        reimbursement_period = (datetime.date(2021, 1, 1), datetime.date(2021, 1, 15))
        payments = repository.find_all_offerer_payments(offerer.id, reimbursement_period)

        # Then
        assert len(payments) == 1
        assert payment_1.booking.token in payments[0]
        assert venue_1.name in payments[0]
