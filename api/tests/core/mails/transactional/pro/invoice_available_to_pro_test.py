from datetime import date

import pytest

from pcapi.core.finance import factories
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.pro.invoice_available_to_pro import send_invoice_available_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories
from pcapi.core.testing import override_features


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueProAvailableInvoiceEmailDataTest:
    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_send_email_in_first_half_of_month(self):
        reimbursement_point = offerers_factories.VenueFactory(bookingEmail="pro@example.com")
        invoice = factories.InvoiceFactory(reimbursementPoint=reimbursement_point, amount=-1000, date=date(2023, 3, 7))
        batch = factories.CashflowBatchFactory(cutoff=date(2023, 2, 28))

        send_invoice_available_to_pro_email(invoice, batch)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value.__dict__
        assert mails_testing.outbox[0]["To"] == "pro@example.com"
        assert mails_testing.outbox[0]["params"] == {
            "MONTANT_REMBOURSEMENT": 10,
            "PERIODE_DEBUT": "16-02-2023",
            "PERIODE_FIN": "28-02-2023",
        }

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_send_email_in_second_half_of_month(self):
        reimbursement_point = offerers_factories.VenueFactory(bookingEmail="pro@example.com")
        invoice = factories.InvoiceFactory(reimbursementPoint=reimbursement_point, amount=-1000, date=date(2023, 7, 20))
        batch = factories.CashflowBatchFactory(cutoff=date(2023, 7, 15))

        send_invoice_available_to_pro_email(invoice, batch)

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value.__dict__
        assert mails_testing.outbox[0]["To"] == "pro@example.com"
        assert mails_testing.outbox[0]["params"] == {
            "MONTANT_REMBOURSEMENT": 10,
            "PERIODE_DEBUT": "01-07-2023",
            "PERIODE_FIN": "15-07-2023",
        }

    @override_features(WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY=False)
    def test_fail_silently_if_no_booking_email(self):
        reimbursement_point = offerers_factories.VenueFactory(bookingEmail=None)
        invoice = factories.InvoiceFactory(reimbursementPoint=reimbursement_point, amount=-1000)
        batch = factories.CashflowBatchFactory()

        send_invoice_available_to_pro_email(invoice, batch)

        assert len(mails_testing.outbox) == 0
