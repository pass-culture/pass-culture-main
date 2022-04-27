import pytest

from pcapi.core.categories import subcategories
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.pro.first_venue_approved_offer_to_pro import (
    get_first_venue_approved_offer_email_data,
)
from pcapi.core.mails.transactional.pro.first_venue_approved_offer_to_pro import (
    send_first_venue_approved_offer_email_to_pro,
)
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.settings import PRO_URL
from pcapi.utils.human_ids import humanize


pytestmark = pytest.mark.usefixtures("db_session")


class SendinblueSendFirstVenueOfferEmailTest:
    def test_get_first_venue_approved_offer_correct_email_metadata(self):
        # Given
        offer = offers_factories.OfferFactory(name="Ma petite offre", venue__name="Mon stade")

        # When
        new_offer_validation_email = get_first_venue_approved_offer_email_data(offer)

        # Then
        assert new_offer_validation_email.template == TransactionalEmail.FIRST_VENUE_APPROVED_OFFER_TO_PRO.value
        assert new_offer_validation_email.params == {
            "OFFER_NAME": "Ma petite offre",
            "VENUE_NAME": "Mon stade",
            "IS_EVENT": False,
            "IS_THING": True,
            "IS_DIGITAL": False,
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/{humanize(offer.id)}/individuel/edition",
            "WITHDRAWAL_PERIOD": 30,
        }

    def test_get_first_venue_approved_book_offer_correct_email_metadata(self):
        # Given
        product = offers_factories.ProductFactory(subcategoryId=subcategories.LIVRE_PAPIER.id)
        offer = offers_factories.OfferFactory(name="Ma petite offre", venue__name="Mon stade", product=product)

        # When
        new_offer_validation_email = get_first_venue_approved_offer_email_data(offer)

        # Then
        assert new_offer_validation_email.template == TransactionalEmail.FIRST_VENUE_APPROVED_OFFER_TO_PRO.value
        assert new_offer_validation_email.params == {
            "OFFER_NAME": "Ma petite offre",
            "VENUE_NAME": "Mon stade",
            "IS_EVENT": False,
            "IS_THING": True,
            "IS_DIGITAL": False,
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/{humanize(offer.id)}/individuel/edition",
            "WITHDRAWAL_PERIOD": 10,
        }

    def test_send_offer_approval_email(self):
        # Given
        venue = offerers_factories.VenueFactory(name="Sibérie orientale", bookingEmail="venue@bookingEmail.com")
        offer = offers_factories.OfferFactory(name="Michel Strogoff", venue=venue)

        # When
        send_first_venue_approved_offer_email_to_pro(offer)

        # Then
        assert len(mails_testing.outbox) == 1  # test number of emails sent
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.FIRST_VENUE_APPROVED_OFFER_TO_PRO.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == "venue@bookingEmail.com"
        assert mails_testing.outbox[0].sent_data["params"] == {
            "OFFER_NAME": offer.name,
            "PC_PRO_OFFER_LINK": f"{PRO_URL}/offre/{humanize(offer.id)}/individuel/edition",
            "VENUE_NAME": venue.name,
            "IS_EVENT": False,
            "IS_THING": True,
            "IS_DIGITAL": False,
            "WITHDRAWAL_PERIOD": 30,
        }
