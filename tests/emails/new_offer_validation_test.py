import pytest

from pcapi import settings
import pcapi.core.offers.factories as offer_factories
from pcapi.emails.new_offer_validation import retrieve_data_for_offer_approval_email
from pcapi.emails.new_offer_validation import retrieve_data_for_offer_rejection_email
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class MakeNewOfferValidationEmailTest:
    def test_approval_email(self):
        # Given
        offer = offer_factories.OfferFactory(name="Ma petite offre", venue__name="Mon stade")

        # When
        new_offer_validation_email = retrieve_data_for_offer_approval_email(offer)

        # Then
        assert new_offer_validation_email == {
            "MJ-TemplateID": 2613721,
            "MJ-TemplateLanguage": True,
            "FromEmail": "offer_validation@example.com",
            "Vars": {
                "offer_name": "Ma petite offre",
                "venue_name": "Mon stade",
                "pc_pro_offer_link": f"{settings.PRO_URL}/offres/{humanize(offer.id)}/edition",
            },
        }

    def test_rejection_email(self):
        # Given
        offer = offer_factories.OfferFactory(name="Ma petite offre", venue__name="Mon stade")

        # When
        new_offer_validation_email = retrieve_data_for_offer_rejection_email(offer)

        # Then
        assert new_offer_validation_email == {
            "MJ-TemplateID": 2613942,
            "FromEmail": "offer_validation@example.com",
            "MJ-TemplateLanguage": True,
            "Vars": {
                "offer_name": "Ma petite offre",
                "venue_name": "Mon stade",
                "pc_pro_offer_link": f"{settings.PRO_URL}/offres/{humanize(offer.id)}/edition",
            },
        }
