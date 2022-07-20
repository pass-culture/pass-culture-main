import pytest

from pcapi.core.finance import factories
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.pro.invoice_available_to_pro import send_invoice_available_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueProAvailableInvoiceEmailDataTest:
    def test_send_emails_available_invoice_to_pro_user(self):
        # given
        business_unit = factories.BusinessUnitFactory()
        invoice = factories.InvoiceFactory(businessUnit=business_unit, amount=-1000)
        offerers_factories.VenueFactory(
            businessUnit=business_unit, bookingEmail="pro@example.com", siret=business_unit.siret
        )

        # when
        send_invoice_available_to_pro_email(invoice)

        # then
        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == "pro@example.com"
        assert mails_testing.outbox[0].sent_data["params"] == {
            "MONTANT_REMBOURSEMENT": 10,
        }

    def test_send_emails_available_invoice_to_pro_user_no_booking_email(self):
        # given
        business_unit = factories.BusinessUnitFactory()
        invoice = factories.InvoiceFactory(businessUnit=business_unit)
        offerers_factories.VenueFactory(businessUnit=business_unit, siret=business_unit.siret, bookingEmail=None)

        # when
        send_invoice_available_to_pro_email(invoice)

        # then
        assert len(mails_testing.outbox) == 0

    def test_send_emails_available_invoice_to_pro_user_no_venue(self):
        # given
        business_unit = factories.BusinessUnitFactory()
        invoice = factories.InvoiceFactory(businessUnit=business_unit)

        # when
        send_invoice_available_to_pro_email(invoice)

        # then
        assert len(mails_testing.outbox) == 0
