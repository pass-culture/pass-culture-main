import pytest

from pcapi.core.finance import factories
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.pro.invoice_available_to_pro import send_invoice_available_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueProAvailableInvoiceEmailDataTest:
    def test_send_email(self):
        reimbursement_point = offerers_factories.VenueFactory(bookingEmail="pro@example.com")
        invoice = factories.InvoiceFactory(reimbursementPoint=reimbursement_point, amount=-1000)

        send_invoice_available_to_pro_email(invoice)

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == "pro@example.com"
        assert mails_testing.outbox[0].sent_data["params"] == {
            "MONTANT_REMBOURSEMENT": 10,
        }

    def test_fail_silently_if_no_booking_email(self):
        reimbursement_point = offerers_factories.VenueFactory(bookingEmail=None)
        invoice = factories.InvoiceFactory(reimbursementPoint=reimbursement_point, amount=-1000)

        send_invoice_available_to_pro_email(invoice)

        assert len(mails_testing.outbox) == 0
