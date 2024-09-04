from datetime import datetime
from datetime import timedelta

import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.utils import human_ids

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class GetEventTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{event_id}"
    endpoint_method = "get"
    default_path_params = {"event_id": 1}

    num_queries_with_error = 1  # retrieve API key
    num_queries_with_error += 1  # retrieve offer
    num_queries_with_error += 1  # retrieve feature_flags for api key validation
    num_queries = num_queries_with_error + 1  # future_offer (a backref)

    def setup_base_resource(self, venue=None) -> offers_models.Offer:
        venue = venue or self.setup_venue()
        product = offers_factories.ProductFactory(thumbCount=1)
        return offers_factories.EventOfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            venue=venue,
            extraData=None,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            product=product,
            idAtProvider="Oh le bel id <3",
        )

    def test_should_raise_404_because_has_no_access_to_venue(self, client: TestClient):
        plain_api_key, _ = self.setup_provider()
        event_offer_id = self.setup_base_resource().id

        # 1. api_key
        # 2. feature
        # 3. offer
        with testing.assert_num_queries(self.num_queries_with_error):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event_offer_id))
            assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self, client: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        event_offer_id = self.setup_base_resource(venue_provider.venue).id

        # 1. api_key
        # 2. feature
        # 3. offer
        with testing.assert_num_queries(self.num_queries_with_error):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event_offer_id))
            assert response.status_code == 404

    def test_get_event(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = self.setup_base_resource(venue=venue_provider.venue)
        event_offer_id = event_offer.id

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event_offer_id))

        assert response.status_code == 200
        assert response.json == {
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "visualDisabilityCompliant": False,
            },
            "bookingContact": None,
            "bookingEmail": None,
            "categoryRelatedFields": {"author": None, "category": "SEANCE_CINE", "stageDirector": None, "visa": None},
            "publicationDate": None,
            "description": "Un livre de contrepèterie",
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": None,
            "eventDuration": None,
            "id": event_offer.id,
            "image": {
                "credit": None,
                "url": f"http://localhost/storage/thumbs/products/{human_ids.humanize(event_offer.product.id)}",
            },
            "itemCollectionDetails": None,
            "location": {"type": "physical", "venueId": event_offer.venueId},
            "name": "Vieux motard que jamais",
            "status": "SOLD_OUT",
            "hasTicket": False,
            "priceCategories": [],
            "idAtProvider": "Oh le bel id <3",
        }

    def test_get_future_event(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = self.setup_base_resource(venue=venue_provider.venue)
        event_offer_id = event_offer.id

        publication_date = datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(days=30)
        offers_factories.FutureOfferFactory(
            offerId=event_offer_id,
            publicationDate=publication_date,
        )

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event_offer_id))

        assert response.status_code == 200
        assert response.json["publicationDate"] == publication_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    def test_event_with_not_selectable_category_can_be_retrieved(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            subcategoryId=subcategories.DECOUVERTE_METIERS.id,
        )
        event_offer_id = event_offer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event_offer_id))

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"]["category"] == "DECOUVERTE_METIERS"

    def test_get_event_without_ticket(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer_id = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            venue=venue_provider.venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.ON_SITE,
        ).id

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event_offer_id))
            assert response.status_code == 200

        assert response.json["hasTicket"] is False

    def test_get_music_offer_without_music_type(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer_id = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            extraData=None,
            venue=venue_provider.venue,
        ).id

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event_offer_id))
            assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {
            "author": None,
            "category": "CONCERT",
            "performer": None,
            "musicType": None,
        }

    def test_ticket_collection_in_app(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer_id = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        ).id

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event_offer_id))
            assert response.status_code == 200

        assert response.json["hasTicket"] == True

    def test_ticket_collection_no_ticket(self, client):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        event_offer_id = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.NO_TICKET,
        ).id

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(plain_api_key).get(self.endpoint_url.format(event_id=event_offer_id))
            assert response.status_code == 200

        assert response.json["hasTicket"] == False
