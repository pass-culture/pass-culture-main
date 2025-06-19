from datetime import datetime
from datetime import timedelta

import pytest
import time_machine

import pcapi.core.educational.factories as educational_factories
import pcapi.core.mails.testing as mails_testing
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.core.mails.transactional.pro.offer_validation_to_pro import get_email_data_from_offer
from pcapi.core.mails.transactional.pro.offer_validation_to_pro import retrieve_data_for_offer_approval_email
from pcapi.core.mails.transactional.pro.offer_validation_to_pro import retrieve_data_for_offer_rejection_email
from pcapi.core.mails.transactional.pro.offer_validation_to_pro import send_offer_validation_status_update_email
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.models import OfferValidationStatus
from pcapi.settings import PRO_URL


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueSendOfferValidationTest:
    @time_machine.travel("2032-10-15 12:48:00")
    @pytest.mark.parametrize("factory_class", [offers_factories.DigitalOfferFactory, offers_factories.OfferFactory])
    def test_get_validation_approval_correct_email_metadata(self, factory_class):
        # Given
        offer = factory_class(name="Ma petite offre", venue__name="Mon stade")
        # When
        new_offer_validation_email = retrieve_data_for_offer_approval_email(offer)

        # Then
        assert new_offer_validation_email.template == TransactionalEmail.OFFER_APPROVAL_TO_PRO.value
        assert new_offer_validation_email.params == {
            "OFFER_NAME": "Ma petite offre",
            "PUBLICATION_DATE": "vendredi 15 octobre 2032",
            "VENUE_NAME": "Mon stade",
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/individuelle/{offer.id}/recapitulatif",
            "OFFER_ADDRESS": offer.fullAddress,
        }

    @time_machine.travel("2032-10-15 12:48:00")
    def test_get_validation_approval_correct_email_metadata_when_future_offer(self):
        # Given
        publication_date = datetime.utcnow() + timedelta(days=30)
        offer = offers_factories.OfferFactory(
            name="Ma petite offre", venue__name="Mon stade", publicationDatetime=publication_date
        )

        # When
        new_offer_validation_email = retrieve_data_for_offer_approval_email(offer)

        # Then
        assert new_offer_validation_email.template == TransactionalEmail.OFFER_APPROVAL_TO_PRO.value
        assert new_offer_validation_email.params == {
            "OFFER_NAME": "Ma petite offre",
            "PUBLICATION_DATE": "dimanche 14 novembre 2032",
            "VENUE_NAME": "Mon stade",
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/individuelle/{offer.id}/recapitulatif",
            "OFFER_ADDRESS": offer.fullAddress,
        }

    @time_machine.travel("2032-10-15 12:48:00")
    def test_send_offer_approval_email(
        self,
    ):
        # Given
        venue = offerers_factories.VenueFactory(name="Sibérie orientale")
        offer = offers_factories.OfferFactory(name="Michel Strogoff", venue=venue)

        # When
        send_offer_validation_status_update_email(
            get_email_data_from_offer(offer, offer.validation, OfferValidationStatus.APPROVED),
            ["jules.verne@example.com"],
        )

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.OFFER_APPROVAL_TO_PRO.value.__dict__
        assert mails_testing.outbox[0]["To"] == "jules.verne@example.com"
        assert mails_testing.outbox[0]["params"] == {
            "OFFER_NAME": offer.name,
            "PUBLICATION_DATE": "vendredi 15 octobre 2032",
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/individuelle/{offer.id}/recapitulatif",
            "VENUE_NAME": venue.name,
            "OFFER_ADDRESS": offer.fullAddress,
        }

    def test_get_validation_rejection_correct_email_metadata(self):
        # Given
        offer = offers_factories.OfferFactory(name="Ma petite offre", venue__name="Mon stade")

        # When
        new_offer_validation_email = retrieve_data_for_offer_rejection_email(offer)

        # Then
        assert new_offer_validation_email.template == TransactionalEmail.OFFER_REJECTION_TO_PRO.value
        assert new_offer_validation_email.params == {
            "IS_COLLECTIVE_OFFER": False,
            "OFFER_NAME": "Ma petite offre",
            "VENUE_NAME": "Mon stade",
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/individuelle/{offer.id}/recapitulatif",
            "OFFER_ADDRESS": offer.fullAddress,
        }

    def test_get_validation_rejection_correct_collective_attribute(self):
        # Given
        offer = educational_factories.CollectiveOfferFactory()

        # When
        new_offer_validation_email = retrieve_data_for_offer_rejection_email(offer)

        # Then
        assert new_offer_validation_email.template == TransactionalEmail.OFFER_REJECTION_TO_PRO.value
        assert new_offer_validation_email.params["IS_COLLECTIVE_OFFER"] is True
        assert new_offer_validation_email.params["OFFER_ADDRESS"] is None

    def test_get_validation_rejection_correct_collective_template_attribute(self):
        # Given
        offer = educational_factories.CollectiveOfferTemplateFactory()

        # When
        new_offer_validation_email = retrieve_data_for_offer_rejection_email(offer)

        # Then
        assert new_offer_validation_email.template == TransactionalEmail.OFFER_REJECTION_TO_PRO.value
        assert new_offer_validation_email.params["IS_COLLECTIVE_OFFER"] is True
        assert new_offer_validation_email.params["OFFER_ADDRESS"] is None

    @time_machine.travel("2032-10-15 12:48:00")
    def test_send_validated_offer_rejection_email(
        self,
    ):
        # Given
        venue = offerers_factories.VenueFactory(name="Sibérie orientale")
        offer = offers_factories.OfferFactory(
            name="Michel Strogoff", venue=venue, validation=OfferValidationStatus.APPROVED
        )

        # When
        send_offer_validation_status_update_email(
            get_email_data_from_offer(offer, offer.validation, OfferValidationStatus.REJECTED),
            ["jules.verne@example.com"],
        )

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert (
            mails_testing.outbox[0]["template"] == TransactionalEmail.OFFER_VALIDATED_TO_REJECTED_TO_PRO.value.__dict__
        )
        assert mails_testing.outbox[0]["To"] == "jules.verne@example.com"
        assert mails_testing.outbox[0]["params"] == {
            "IS_COLLECTIVE_OFFER": False,
            "OFFER_NAME": offer.name,
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/individuelle/{offer.id}/recapitulatif",
            "CREATION_DATE": "vendredi 15 octobre 2032",
        }

    def test_send_pending_offer_rejection_email(
        self,
    ):
        # Given
        venue = offerers_factories.VenueFactory(name="Sibérie orientale")
        offer = offers_factories.OfferFactory(
            name="Michel Strogoff", venue=venue, validation=OfferValidationStatus.PENDING
        )

        # When
        send_offer_validation_status_update_email(
            get_email_data_from_offer(offer, offer.validation, OfferValidationStatus.REJECTED),
            ["jules.verne@example.com"],
        )

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.OFFER_PENDING_TO_REJECTED_TO_PRO.value.__dict__
        assert mails_testing.outbox[0]["To"] == "jules.verne@example.com"
        assert mails_testing.outbox[0]["params"] == {
            "IS_COLLECTIVE_OFFER": False,
            "OFFER_NAME": offer.name,
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/individuelle/{offer.id}/recapitulatif",
            "VENUE_NAME": venue.name,
        }

    def test_send_other_offer_rejection_email(
        self,
    ):
        # Given
        venue = offerers_factories.VenueFactory(name="Sibérie orientale")
        offer = offers_factories.OfferFactory(
            name="Michel Strogoff", venue=venue, validation=OfferValidationStatus.DRAFT
        )

        # When
        send_offer_validation_status_update_email(
            get_email_data_from_offer(offer, offer.validation, OfferValidationStatus.REJECTED),
            ["jules.verne@example.com"],
        )

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.OFFER_REJECTION_TO_PRO.value.__dict__
        assert mails_testing.outbox[0]["To"] == "jules.verne@example.com"
        assert mails_testing.outbox[0]["params"] == {
            "IS_COLLECTIVE_OFFER": False,
            "OFFER_NAME": offer.name,
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/individuelle/{offer.id}/recapitulatif",
            "VENUE_NAME": venue.name,
            "OFFER_ADDRESS": offer.fullAddress,
        }
