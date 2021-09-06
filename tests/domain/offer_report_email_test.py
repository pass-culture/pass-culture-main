import pytest

from pcapi import settings
import pcapi.core.mails.testing as mails_testing
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.models import Reason
from pcapi.core.users.factories import BeneficiaryFactory
from pcapi.domain.offer_report_emails import send_report_notification


pytestmark = pytest.mark.usefixtures("db_session")


class OfferReportEmailTest:
    def test_report_other(self):
        # Given
        user = BeneficiaryFactory()
        offer = OfferFactory()
        reason = Reason.OTHER.value

        # When
        send_report_notification(user, offer, reason, "blabla")

        # Then
        assert mails_testing.outbox[0].sent_data["To"] == settings.SUPPORT_EMAIL_ADDRESS

    def test_report_inappropriate(self):
        # Given
        user = BeneficiaryFactory()
        offer = OfferFactory()
        reason = Reason.INAPPROPRIATE.value

        # When
        send_report_notification(user, offer, reason, "blabla")

        # Then
        assert mails_testing.outbox[0].sent_data["To"] == settings.REPORT_OFFER_EMAIL_ADDRESS
