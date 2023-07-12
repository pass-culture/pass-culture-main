from datetime import date

import pytest

from pcapi.core.finance import factories
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.pro.invoice_available_to_pro import send_invoice_available_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueProAvailableInvoiceEmailDataTest:
    def test_send_email_in_first_half_of_month(self):
        reimbursement_point = offerers_factories.VenueFactory(bookingEmail="pro@example.com")
        invoice = factories.InvoiceFactory(reimbursementPoint=reimbursement_point, amount=-1000, date=date(2023, 3, 7))

        send_invoice_available_to_pro_email(invoice)

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == "pro@example.com"
        assert mails_testing.outbox[0].sent_data["params"] == {
            "MONTANT_REMBOURSEMENT": 10,
            "PERIODE_DEBUT": "16-02-2023",
            "PERIODE_FIN": "28-02-2023",
        }

    def test_send_email_in_second_half_of_month(self):
        reimbursement_point = offerers_factories.VenueFactory(bookingEmail="pro@example.com")
        invoice = factories.InvoiceFactory(reimbursementPoint=reimbursement_point, amount=-1000, date=date(2023, 7, 20))

        send_invoice_available_to_pro_email(invoice)

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == "pro@example.com"
        assert mails_testing.outbox[0].sent_data["params"] == {
            "MONTANT_REMBOURSEMENT": 10,
            "PERIODE_DEBUT": "01-07-2023",
            "PERIODE_FIN": "15-07-2023",
        }

    def test_fail_silently_if_no_booking_email(self):
        reimbursement_point = offerers_factories.VenueFactory(bookingEmail=None)
        invoice = factories.InvoiceFactory(reimbursementPoint=reimbursement_point, amount=-1000)

        send_invoice_available_to_pro_email(invoice)

        assert len(mails_testing.outbox) == 0
