import decimal

import freezegun
import pytest

from pcapi import settings
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import models as offers_models
from pcapi.models import offer_mixin
from pcapi.utils import human_ids

from tests.routes import image_data

from . import utils


@pytest.mark.usefixtures("db_session")
class PostEventTest:
    def test_event_minimal_body(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "RENCONTRE"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.name == "Le champ des possibles"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "RENCONTRE"
        assert created_offer.audioDisabilityCompliant is True
        assert created_offer.lastProvider.name == "Technical provider"
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert not created_offer.isDuo
        assert created_offer.extraData == {}
        assert created_offer.bookingEmail is None
        assert created_offer.description is None
        assert created_offer.status == offer_mixin.OfferStatus.SOLD_OUT
        assert created_offer.withdrawalDetails is None
        assert created_offer.withdrawalType is None
        assert created_offer.withdrawalDelay is None

    @freezegun.freeze_time("2022-01-01 12:00:00")
    def test_event_creation_with_full_body(self, client, clear_tests_assets_bucket):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "enableDoubleBookings": True,
                "bookingContact": "contact@example.com",
                "bookingEmail": "nicoj@example.com",
                "categoryRelatedFields": {
                    "author": "Ray Charles",
                    "category": "CONCERT",
                    "musicType": "ELECTRO-HOUSE",
                    "performer": "Nicolas Jaar",
                    "stageDirector": "Alfred",  # field not applicable
                },
                "description": "Space is only noise if you can see",
                "eventDuration": 120,
                "accessibility": {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": True,
                    "motorDisabilityCompliant": True,
                    "visualDisabilityCompliant": True,
                },
                "externalTicketOfficeUrl": "https://maposaic.com",
                "image": {
                    "credit": "Jean-Crédit Photo",
                    "file": image_data.GOOD_IMAGE,
                },
                "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Nicolas Jaar dans ton salon",
                "ticketCollection": {"way": "by_email", "daysBeforeEvent": 1},
                "priceCategories": [{"price": 2500, "label": "triangle or"}],
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.lastProvider.name == "Technical provider"
        assert created_offer.name == "Nicolas Jaar dans ton salon"
        assert created_offer.venue == venue
        assert created_offer.subcategoryId == "CONCERT"
        assert created_offer.audioDisabilityCompliant is False
        assert created_offer.mentalDisabilityCompliant is True
        assert created_offer.motorDisabilityCompliant is True
        assert created_offer.visualDisabilityCompliant is True
        assert created_offer.isDuo is True
        assert created_offer.extraData == {
            "author": "Ray Charles",
            "musicType": "880",
            "musicSubType": "894",
            "performer": "Nicolas Jaar",
        }
        assert created_offer.bookingEmail == "nicoj@example.com"
        assert created_offer.description == "Space is only noise if you can see"
        assert created_offer.externalTicketOfficeUrl == "https://maposaic.com"
        assert created_offer.status == offer_mixin.OfferStatus.SOLD_OUT
        assert created_offer.withdrawalDetails == "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2"
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.BY_EMAIL
        assert created_offer.withdrawalDelay == 86400

        created_mediation = offers_models.Mediation.query.one()
        assert created_mediation.offer == created_offer
        assert created_offer.image.url == created_mediation.thumbUrl
        assert (
            created_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(created_mediation.id)}"
        )

        created_price_category = offers_models.PriceCategory.query.one()
        assert created_price_category.price == decimal.Decimal("25")
        assert created_price_category.label == "triangle or"

        assert response.json == {
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": True,
                "motorDisabilityCompliant": True,
                "visualDisabilityCompliant": True,
            },
            "bookingContact": "contact@example.com",
            "bookingEmail": "nicoj@example.com",
            "categoryRelatedFields": {
                "author": "Ray Charles",
                "category": "CONCERT",
                "musicType": "ELECTRO-HOUSE",
                "performer": "Nicolas Jaar",
            },
            "description": "Space is only noise if you can see",
            "enableDoubleBookings": True,
            "eventDuration": 120,
            "externalTicketOfficeUrl": "https://maposaic.com",
            "id": created_offer.id,
            "image": {
                "credit": "Jean-Crédit Photo",
                "url": f"http://localhost/storage/thumbs/mediations/{human_ids.humanize(created_mediation.id)}",
            },
            "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
            "location": {"type": "physical", "venueId": venue.id},
            "name": "Nicolas Jaar dans ton salon",
            "status": "SOLD_OUT",
            "ticketCollection": {"daysBeforeEvent": 1, "way": "by_email"},
            "priceCategories": [{"id": created_price_category.id, "price": 2500, "label": "triangle or"}],
        }

    @pytest.mark.usefixtures("db_session")
    def test_other_music_type_serialization(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "CONCERT", "musicType": "OTHER"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "bookingContact": "booking@conta.ct",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.extraData == {"musicType": "-1", "musicSubType": "-1"}

        assert response.json["categoryRelatedFields"] == {
            "author": None,
            "category": "CONCERT",
            "musicType": "OTHER",
            "performer": None,
        }

    def test_event_without_ticket(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "ticketCollection": None,
                "bookingContact": "booking@conta.ct",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.NO_TICKET

    def test_event_with_on_site_ticket(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "ticketCollection": {"way": "on_site", "minutesBeforeEvent": 30},
                "bookingContact": "booking@conta.ct",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.ON_SITE
        assert created_offer.withdrawalDelay == 30 * 60

    def test_event_with_email_ticket(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "ticketCollection": {"way": "by_email", "daysBeforeEvent": 3},
                "bookingContact": "booking@conta.ct",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.BY_EMAIL
        assert created_offer.withdrawalDelay == 3 * 24 * 3600

    def test_error_when_ticket_specified_but_not_applicable(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "EVENEMENT_PATRIMOINE"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "ticketCollection": {"way": "on_site", "minutesBeforeEvent": 30},
            },
        )

        assert response.status_code == 400
        assert offers_models.Offer.query.count() == 0
        assert response.json == {
            "offer": ["Une offre qui n'a pas de ticket retirable ne peut pas avoir un type de retrait renseigné"]
        }

    def test_error_when_withdrawable_event_but_no_booking_contact(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "ticketCollection": {"way": "by_email", "daysBeforeEvent": 3},
            },
        )

        assert response.status_code == 400
        assert offers_models.Offer.query.count() == 0
        assert response.json == {
            "offer": ["Une offre qui a un ticket retirable doit avoir l'email du contact de réservation"]
        }
