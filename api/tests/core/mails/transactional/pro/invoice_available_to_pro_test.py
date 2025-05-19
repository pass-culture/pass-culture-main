import datetime

import pytest

import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.finance import factories
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.pro.invoice_available_to_pro import send_invoice_available_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueProAvailableInvoiceEmailDataTest:
    def test_send_email_in_first_half_of_month(self):
        bank_account = factories.BankAccountFactory()

        offerers_factories.VenueBankAccountLinkFactory(
            venue__bookingEmail="pro@example.com", bankAccount=bank_account, timespan=(datetime.datetime(2023, 2, 19),)
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue__bookingEmail="pro@example.com", bankAccount=bank_account, timespan=(datetime.datetime(2023, 2, 19),)
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue__bookingEmail="other_pro@example.com",
            bankAccount=bank_account,
            timespan=(datetime.datetime(2023, 2, 19),),
        )

        invoice = factories.InvoiceFactory(bankAccount=bank_account, amount=-1000, date=datetime.date(2023, 3, 7))
        batch = factories.CashflowBatchFactory(cutoff=datetime.datetime(2023, 2, 28, 23))  # winter time

        send_invoice_available_to_pro_email(invoice, batch)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value.__dict__
        assert len(mails_testing.outbox[0]["To"].split(", ")) == 2
        assert set(mails_testing.outbox[0]["To"].split(", ")) == {"other_pro@example.com", "pro@example.com"}
        assert mails_testing.outbox[0]["params"] == {
            "MONTANT_REMBOURSEMENT": 10,
            "FORMATTED_MONTANT_REMBOURSEMENT": "10 €",
            "PERIODE_DEBUT": "jeudi 16 février 2023",
            "PERIODE_FIN": "mardi 28 février 2023",
        }

    def test_send_email_in_second_half_of_month(self):
        bank_account = factories.BankAccountFactory()

        offerers_factories.VenueBankAccountLinkFactory(
            venue__bookingEmail="pro@example.com", bankAccount=bank_account, timespan=(datetime.datetime(2023, 2, 19),)
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue__bookingEmail="pro@example.com", bankAccount=bank_account, timespan=(datetime.datetime(2023, 2, 19),)
        )
        offerers_factories.VenueBankAccountLinkFactory(
            venue__bookingEmail="other_pro@example.com",
            bankAccount=bank_account,
            timespan=(datetime.datetime(2023, 6, 25), datetime.datetime(2023, 7, 12)),
        )

        invoice = factories.InvoiceFactory(bankAccount=bank_account, amount=-1000, date=datetime.date(2023, 7, 20))
        batch = factories.CashflowBatchFactory(cutoff=datetime.datetime(2023, 7, 15, 22))  # summer time

        send_invoice_available_to_pro_email(invoice, batch)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value.__dict__
        assert len(mails_testing.outbox[0]["To"].split(", ")) == 1
        assert set(mails_testing.outbox[0]["To"].split(", ")) == {"pro@example.com"}
        assert mails_testing.outbox[0]["params"] == {
            "MONTANT_REMBOURSEMENT": 10,
            "FORMATTED_MONTANT_REMBOURSEMENT": "10 €",
            "PERIODE_DEBUT": "samedi 1er juillet 2023",
            "PERIODE_FIN": "samedi 15 juillet 2023",
        }

    def test_fail_silently_if_no_booking_email(self):
        bank_account = factories.BankAccountFactory()
        offerers_factories.VenueBankAccountLinkFactory(
            venue__bookingEmail=None,
            bankAccount=bank_account,
        )
        invoice = factories.InvoiceFactory(bankAccount=bank_account, amount=-1000)
        batch = factories.CashflowBatchFactory()

        send_invoice_available_to_pro_email(invoice, batch)

        assert len(mails_testing.outbox) == 0
