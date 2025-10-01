from datetime import datetime
from datetime import timedelta
from datetime import timezone

import pytest
import time_machine

from pcapi.core import testing
from pcapi.core.categories import subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models

from tests.conftest import TestClient
from tests.routes.public.helpers import PublicAPIVenueEndpointHelper


@pytest.mark.usefixtures("db_session")
class GetEventTest(PublicAPIVenueEndpointHelper):
    endpoint_url = "/public/offers/v1/events/{offer_id}"
    endpoint_method = "get"
    default_path_params = {"offer_id": 1}

    num_queries_with_error = 1  # retrieve API key
    num_queries_with_error += 1  # retrieve offer
    num_queries_with_error += 1  # rollback atomic
    num_queries_with_error += 1  # rollback atomic

    num_queries = 1  # retrieve API key
    num_queries += 1  # # retrieve offer
    num_queries += 1  # fetch stocks
    num_queries += 1  # fetch mediations
    num_queries += 1  # fetch price categories

    num_queries_full = num_queries + 1  # fetch product

    def setup_base_resource(self, venue=None, **offer_kwargs) -> offers_models.Offer:
        venue = venue or self.setup_venue()
        product = offers_factories.ProductFactory(
            description="Un livre de contrepèterie",
            subcategoryId=subcategories.SEANCE_CINE.id,
            name="Vieux motard que jamais",
            extraData=None,
        )
        offers_factories.ProductMediationFactory(product=product)

        offer_kwargs = offer_kwargs if offer_kwargs else {}
        return offers_factories.EventOfferFactory(
            venue=venue, product=product, idAtProvider="Oh le bel id <3", **offer_kwargs
        )

    def test_should_raise_404_because_has_no_access_to_venue(self: TestClient):
        plain_api_key, _ = self.setup_provider()
        offer_id = self.setup_base_resource().id

        with testing.assert_num_queries(self.num_queries_with_error):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 404

    def test_should_raise_404_because_venue_provider_is_inactive(self: TestClient):
        plain_api_key, venue_provider = self.setup_inactive_venue_provider()
        offer_id = self.setup_base_resource(venue_provider.venue).id

        with testing.assert_num_queries(self.num_queries_with_error):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 404

    @time_machine.travel(datetime(2025, 6, 25, 12, 30, tzinfo=timezone.utc), tick=False)
    def test_get_event(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = self.setup_base_resource(venue=venue_provider.venue)
        offer_id = offer.id

        with testing.assert_num_queries(self.num_queries_full):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json == {
            "accessibility": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "visualDisabilityCompliant": False,
            },
            "bookingAllowedDatetime": None,
            "bookingContact": None,
            "bookingEmail": None,
            "categoryRelatedFields": {"author": None, "category": "SEANCE_CINE", "stageDirector": None, "visa": None},
            "description": "Un livre de contrepèterie",
            "enableDoubleBookings": False,
            "externalTicketOfficeUrl": None,
            "eventDuration": None,
            "id": offer.id,
            "image": {
                "credit": None,
                "url": f"http://localhost/storage/thumbs/{offer.product.productMediations[0].uuid}",
            },
            "itemCollectionDetails": None,
            "location": {"type": "physical", "venueId": offer.venueId},
            "name": "Vieux motard que jamais",
            "status": "SOLD_OUT",
            "hasTicket": False,
            "priceCategories": [],
            "publicationDatetime": "2025-06-25T12:25:00Z",
            "idAtProvider": "Oh le bel id <3",
        }

    def test_get_future_event(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()

        publication_date = datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(days=30)
        offer = self.setup_base_resource(venue=venue_provider.venue, publicationDatetime=publication_date)
        offer_id = offer.id

        with testing.assert_num_queries(self.num_queries_full):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})

        assert response.status_code == 200
        assert response.json["publicationDatetime"] == publication_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    def test_event_with_not_selectable_category_can_be_retrieved(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            subcategoryId=subcategories.DECOUVERTE_METIERS.id,
        )
        offer_id = offer.id
        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})

        assert response.status_code == 200
        assert response.json["categoryRelatedFields"]["category"] == "DECOUVERTE_METIERS"

    def test_get_event_without_ticket(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer_id = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            venue=venue_provider.venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.ON_SITE,
        ).id

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json["hasTicket"] is False

    def test_get_music_offer_without_music_type(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer_id = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            extraData=None,
            venue=venue_provider.venue,
        ).id

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 200
        assert response.json["categoryRelatedFields"] == {
            "author": None,
            "category": "CONCERT",
            "performer": None,
            "musicType": None,
        }

    def test_ticket_collection_in_app(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer_id = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        ).id

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json["hasTicket"] == True

    def test_ticket_collection_no_ticket(self):
        plain_api_key, venue_provider = self.setup_active_venue_provider()
        offer_id = offers_factories.EventOfferFactory(
            venue=venue_provider.venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.NO_TICKET,
        ).id

        with testing.assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, path_params={"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json["hasTicket"] == False
