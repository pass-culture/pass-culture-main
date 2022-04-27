import pytest

import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro.offer_validation_to_pro import retrieve_data_for_offer_approval_email
from pcapi.core.mails.transactional.pro.offer_validation_to_pro import retrieve_data_for_offer_rejection_email
from pcapi.core.mails.transactional.pro.offer_validation_to_pro import send_offer_validation_status_update_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.settings import PRO_URL
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueSendOfferValidationTest:
    def test_get_validation_approval_correct_email_metadata(self):
        # Given
        offer = offers_factories.OfferFactory(name="Ma petite offre", venue__name="Mon stade")

        # When
        new_offer_validation_email = retrieve_data_for_offer_approval_email(offer)

        # Then
        assert new_offer_validation_email.template == TransactionalEmail.OFFER_APPROVAL_TO_PRO.value
        assert new_offer_validation_email.params == {
            "OFFER_NAME": "Ma petite offre",
            "VENUE_NAME": "Mon stade",
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/{humanize(offer.id)}/individuel/edition",
        }

    def test_send_offer_approval_email(
        self,
    ):
        # Given
        venue = offerers_factories.VenueFactory(name="Sibérie orientale")
        offer = offers_factories.OfferFactory(name="Michel Strogoff", venue=venue)

        # When
        send_offer_validation_status_update_email(offer, OfferValidationStatus.APPROVED, ["jules.verne@example.com"])

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.OFFER_APPROVAL_TO_PRO.value.__dict__
        assert mails_testing.outbox[0].sent_data["To"] == "jules.verne@example.com"
        assert mails_testing.outbox[0].sent_data["params"] == {
            "OFFER_NAME": offer.name,
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/{humanize(offer.id)}/individuel/edition",
            "VENUE_NAME": venue.name,
        }

    def test_get_validation_rejection_correct_email_metadata(self):
        # Given
        offer = offers_factories.OfferFactory(name="Ma petite offre", venue__name="Mon stade")

        # When
        new_offer_validation_email = retrieve_data_for_offer_rejection_email(offer)

        # Then
        assert new_offer_validation_email.template == TransactionalEmail.OFFER_REJECTION_TO_PRO.value
        assert new_offer_validation_email.params == {
            "OFFER_NAME": "Ma petite offre",
            "VENUE_NAME": "Mon stade",
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/{humanize(offer.id)}/individuel/edition",
        }

    def test_send_offer_rejection_email(
        self,
    ):
        # Given
        venue = offerers_factories.VenueFactory(name="Sibérie orientale")
        offer = offers_factories.OfferFactory(name="Michel Strogoff", venue=venue)

        # When
        send_offer_validation_status_update_email(offer, OfferValidationStatus.REJECTED, ["jules.verne@example.com"])

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0].sent_data["template"] == TransactionalEmail.OFFER_REJECTION_TO_PRO.value.__dict__
        assert mails_testing.outbox[0].sent_data["To"] == "jules.verne@example.com"
        assert mails_testing.outbox[0].sent_data["params"] == {
            "OFFER_NAME": offer.name,
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/{humanize(offer.id)}/individuel/edition",
            "VENUE_NAME": venue.name,
        }
