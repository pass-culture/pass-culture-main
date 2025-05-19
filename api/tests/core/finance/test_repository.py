import datetime

import pytest

import pcapi.core.bookings.factories as bookings_factories
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.users.factories as users_factories
from pcapi.core.finance import factories
from pcapi.core.finance import models
from pcapi.core.finance import repository
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
