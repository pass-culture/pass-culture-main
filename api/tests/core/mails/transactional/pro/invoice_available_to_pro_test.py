from datetime import datetime

import pytest

from pcapi.core.finance import factories
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.pro.invoice_available_to_pro import get_invoice_available_to_pro_email_data
from pcapi.core.mails.transactional.pro.invoice_available_to_pro import send_invoice_available_to_pro_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueProAvailableInvoiceEmailDataTest:
    def test_get_email_correct_metadata(self):
        # Given
        business_unit = factories.BusinessUnitFactory()
        # This date is to test the edge case where the payment has been made the previous century.
        invoice = factories.InvoiceFactory(businessUnit=business_unit, date=datetime(2000, 1, 3), amount=-1000)
        offerers_factories.VenueFactory(businessUnit=business_unit)

        # When
        email_data = get_invoice_available_to_pro_email_data(invoice)

        # Then
        assert email_data.template == TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value

    def test_send_emails_available_invoice_to_pro_user(self):
        # given
        business_unit = factories.BusinessUnitFactory()
        invoice = factories.InvoiceFactory(businessUnit=business_unit, date=datetime(2022, 1, 25), amount=-1000)
        venue = offerers_factories.VenueFactory(
            businessUnit=business_unit, bookingEmail="pro@example.com", siret=business_unit.siret
        )

        # when
        send_invoice_available_to_pro_email(invoice)

        # then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert (
            mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.INVOICE_AVAILABLE_TO_PRO.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == "pro@example.com"
        assert mails_testing.outbox[0].sent_data["params"] == {
            "montant": 10,
        }
