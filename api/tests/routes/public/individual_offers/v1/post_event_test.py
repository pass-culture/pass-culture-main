import decimal

import pytest

from pcapi import settings
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import models as offers_models
from pcapi.core.testing import override_features
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
                "hasTicket": False,
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

    def test_event_creation_with_full_body(self, client, clear_tests_assets_bucket):
        venue, _ = utils.create_offerer_provider_linked_to_venue(with_charlie=True)

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
                "priceCategories": [{"price": 30000, "label": "triangle or"}],
                "hasTicket": True,
                "idAtProvider": "T'as un bel id tu sais",
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
            "gtl_id": "04000000",
            "performer": "Nicolas Jaar",
        }
        assert created_offer.bookingEmail == "nicoj@example.com"
        assert created_offer.description == "Space is only noise if you can see"
        assert created_offer.externalTicketOfficeUrl == "https://maposaic.com"
        assert created_offer.status == offer_mixin.OfferStatus.SOLD_OUT
        assert created_offer.withdrawalDetails == "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2"
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP
        assert created_offer.withdrawalDelay == None
        assert created_offer.idAtProvider == "T'as un bel id tu sais"

        created_mediation = offers_models.Mediation.query.one()
        assert created_mediation.offer == created_offer
        assert created_offer.image.url == created_mediation.thumbUrl
        assert (
            created_offer.image.url
            == f"{settings.OBJECT_STORAGE_URL}/thumbs/mediations/{human_ids.humanize(created_mediation.id)}"
        )

        created_price_category = offers_models.PriceCategory.query.one()
        assert created_price_category.price == decimal.Decimal("300")
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
            "idAtProvider": "T'as un bel id tu sais",
            "image": {
                "credit": "Jean-Crédit Photo",
                "url": f"http://localhost/storage/thumbs/mediations/{human_ids.humanize(created_mediation.id)}",
            },
            "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
            "location": {"type": "physical", "venueId": venue.id},
            "name": "Nicolas Jaar dans ton salon",
            "status": "SOLD_OUT",
            "priceCategories": [{"id": created_price_category.id, "price": 30000, "label": "triangle or"}],
            "hasTicket": True,
        }

    def test_event_creation_with_titelive_type(self, client, clear_tests_assets_bucket):
        venue, _ = utils.create_offerer_provider_linked_to_venue(with_charlie=True)
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "bookingContact": "contact@example.com",
                "categoryRelatedFields": {
                    "author": "Ray Charles",
                    "category": "CONCERT",
                    "musicType": "MUSIQUE_CLASSIQUE",
                    "performer": "Nicolas Jaar",
                },
                "accessibility": {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": True,
                    "motorDisabilityCompliant": True,
                    "visualDisabilityCompliant": True,
                },
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Nicolas Jaar dans ton salon",
                "priceCategories": [{"price": 0, "label": "triangle or"}],
                "hasTicket": False,
            },
        )
        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.subcategoryId == "CONCERT"
        assert created_offer.extraData == {
            "author": "Ray Charles",
            "gtl_id": "01000000",
            "musicType": "600",
            "musicSubType": "-1",
            "performer": "Nicolas Jaar",
        }
        assert response.json["categoryRelatedFields"] == {
            "author": "Ray Charles",
            "category": "CONCERT",
            "musicType": "OTHER",
            "performer": "Nicolas Jaar",
        }

    @override_features(ENABLE_TITELIVE_MUSIC_TYPES_IN_API_OUTPUT=True)
    def test_event_creation_with_titelive_type_with_active_serialization(self, client, clear_tests_assets_bucket):
        venue, _ = utils.create_offerer_provider_linked_to_venue(with_charlie=True)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "bookingContact": "contact@example.com",
                "bookingEmail": "nicoj@example.com",
                "categoryRelatedFields": {
                    "author": "Ray Charles",
                    "category": "CONCERT",
                    "musicType": "JAZZ-BLUES",
                    "performer": "Nicolas Jaar",
                    "stageDirector": "Alfred",  # field not applicable
                },
                "eventDuration": 120,
                "accessibility": {
                    "audioDisabilityCompliant": False,
                    "mentalDisabilityCompliant": True,
                    "motorDisabilityCompliant": True,
                    "visualDisabilityCompliant": True,
                },
                "externalTicketOfficeUrl": "https://maposaic.com",
                "itemCollectionDetails": "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2",
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Nicolas Jaar dans ton salon",
                "priceCategories": [{"price": 30000, "label": "triangle or"}],
                "hasTicket": True,
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.subcategoryId == "CONCERT"
        assert created_offer.extraData == {
            "author": "Ray Charles",
            "gtl_id": "02000000",
            "musicType": "501",
            "musicSubType": "-1",
            "performer": "Nicolas Jaar",
        }
        assert created_offer.externalTicketOfficeUrl == "https://maposaic.com"
        assert created_offer.withdrawalDetails == "A retirer au 6ème sous-sol du parking de la gare entre minuit et 2"
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP

        assert response.json["categoryRelatedFields"] == {
            "author": "Ray Charles",
            "category": "CONCERT",
            "musicType": "JAZZ-BLUES",
            "performer": "Nicolas Jaar",
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
                "hasTicket": False,
                "bookingContact": "booking@conta.ct",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.extraData == {"musicType": "-1", "musicSubType": "-1", "gtl_id": "19000000"}

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
                "hasTicket": False,
                "bookingContact": "booking@conta.ct",
            },
        )

        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.NO_TICKET

    def test_event_with_in_app_ticket(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(with_charlie=True)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "hasTicket": True,
                "bookingContact": "booking@conta.ct",
            },
        )
        assert response.status_code == 200
        created_offer = offers_models.Offer.query.one()
        assert created_offer.withdrawalType == offers_models.WithdrawalTypeEnum.IN_APP

    def test_error_when_withdrawable_event_but_no_booking_contact(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(with_charlie=True)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "hasTicket": True,
            },
        )

        assert response.status_code == 400
        assert offers_models.Offer.query.count() == 0
        assert response.json == {
            "offer": ["Une offre qui a un ticket retirable doit avoir l'email du contact de réservation"]
        }

    def test_error_when_duplicate_price_categories(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "enableDoubleBookings": True,
                "bookingContact": "contact@example.com",
                "bookingEmail": "nicoj@example.com",
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "categoryRelatedFields": {
                    "author": "Ray Charles",
                    "category": "CONCERT",
                    "musicType": "ELECTRO-HOUSE",
                    "gtl_id": "04030000",
                    "performer": "Nicolas Jaar",
                    "stageDirector": "Alfred",  # field not applicable
                },
                "hasTicket": True,
                "priceCategories": [
                    {"price": 2500, "label": "triangle or"},
                    {"price": 12, "label": "triangle argent"},
                    {"price": 100, "label": "triangle bronze"},
                    {"price": 2500, "label": "triangle or"},
                ],
            },
        )

        assert response.status_code == 400
        assert response.json == {"priceCategories": ["Price categories must be unique"]}

    def test_returns_404_for_inactive_venue_provider(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)

        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).post(
            "/public/offers/v1/events",
            json={
                "categoryRelatedFields": {"category": "FESTIVAL_ART_VISUEL"},
                "accessibility": utils.ACCESSIBILITY_FIELDS,
                "location": {"type": "physical", "venueId": venue.id},
                "name": "Le champ des possibles",
                "hasTicket": False,
            },
        )

        assert response.status_code == 404
