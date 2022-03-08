import dataclasses

import pytest

from pcapi import settings
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.mails.transactional.users.reported_offer_by_user import get_reported_offer_email_data
from pcapi.core.mails.transactional.users.reported_offer_by_user import send_email_reported_offer_by_user
from pcapi.core.offers.factories import OfferFactory
from pcapi.core.offers.models import Reason
from pcapi.core.users.factories import BeneficiaryGrant18Factory
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class ReportedOfferByUserEmailTest:
    def test_report_other(self):
        # Given
        user = BeneficiaryGrant18Factory()
        offer = OfferFactory()
        reason = Reason.OTHER.value

        # When
        send_email_reported_offer_by_user(user, offer, reason, "blabla")

        # Then
        assert mails_testing.outbox[0].sent_data["To"] == settings.SUPPORT_EMAIL_ADDRESS
        assert mails_testing.outbox[0].sent_data["template"] == dataclasses.asdict(
            TransactionalEmail.REPORTED_OFFER_BY_USER.value
        )

    def test_report_inappropriate(self):
        # Given
        user = BeneficiaryGrant18Factory()
        offer = OfferFactory()
        reason = Reason.INAPPROPRIATE.value

        # When
        send_email_reported_offer_by_user(user, offer, reason, "blabla")

        # Then
        assert mails_testing.outbox[0].sent_data["To"] == settings.REPORT_OFFER_EMAIL_ADDRESS

    def test_get_email_metadata(self):

        # Given
        user = BeneficiaryGrant18Factory()
        offer = OfferFactory()
        reason = Reason.INAPPROPRIATE.value

        # when
        email_data = get_reported_offer_email_data(user, offer, reason)

        # Then
        assert email_data.template == TransactionalEmail.REPORTED_OFFER_BY_USER.value
        assert email_data.params == {
            "USER_ID": user.id,
            "OFFER_ID": offer.id,
            "OFFER_NAME": offer.name,
            "REASON": "Le contenu est inapproprié",
            "OFFER_URL": "http://localhost:3001/offre/" + f"{humanize(offer.id)}/individuel/edition",
        }
