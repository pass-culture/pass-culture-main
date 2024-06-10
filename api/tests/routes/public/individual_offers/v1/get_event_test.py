import pytest

from pcapi.core import testing
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models
from pcapi.utils import human_ids

from . import utils


@pytest.mark.usefixtures("db_session")
class GetEventTest:
    def test_404_when_requesting_a_product(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.ThingOfferFactory(venue=venue)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(f"/public/offers/v1/events/{event_offer.id}")

            assert response.status_code == 404
            assert response.json == {"event_id": ["The event offer could not be found"]}

    def test_get_event(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        product = offers_factories.ProductFactory(thumbCount=1)
        event_offer = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.SEANCE_CINE.id,
            venue=venue,
            extraData=None,
            description="Un livre de contrepèterie",
            name="Vieux motard que jamais",
            product=product,
            idAtProvider="Oh le bel id <3",
        )
        event_offer_id = event_offer.id

        num_query = 1  # retrieve API key
        num_query += 1  # retrieve offer
        num_query += 1  # retrieve feature_flags for api key validation

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(num_query):
            response = client.get(f"/public/offers/v1/events/{event_offer_id}")

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
                "categoryRelatedFields": {
                    "author": None,
                    "category": "SEANCE_CINE",
                    "stageDirector": None,
                    "visa": None,
                },
                "description": "Un livre de contrepèterie",
                "enableDoubleBookings": False,
                "externalTicketOfficeUrl": None,
                "eventDuration": None,
                "id": event_offer.id,
                "image": {
                    "credit": None,
                    "url": f"http://localhost/storage/thumbs/products/{human_ids.humanize(product.id)}",
                },
                "itemCollectionDetails": None,
                "location": {"type": "physical", "venueId": event_offer.venueId},
                "name": "Vieux motard que jamais",
                "status": "SOLD_OUT",
                "hasTicket": False,
                "priceCategories": [],
                "idAtProvider": "Oh le bel id <3",
            }

    def test_event_with_not_selectable_category_can_be_retrieved(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            subcategoryId=subcategories.DECOUVERTE_METIERS.id,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(f"/public/offers/v1/events/{event_offer.id}")

            assert response.status_code == 200
            assert response.json["categoryRelatedFields"]["category"] == "DECOUVERTE_METIERS"

    def test_get_event_without_ticket(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            venue=venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.ON_SITE,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}"
            )
            assert response.status_code == 200
            assert response.json["hasTicket"] is False

    def test_get_music_offer_without_music_type(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            subcategoryId=subcategories.CONCERT.id,
            extraData=None,
            venue=venue,
        )
        with testing.assert_num_queries(4):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}"
            )
            assert response.status_code == 200
            assert response.json["categoryRelatedFields"] == {
                "author": None,
                "category": "CONCERT",
                "performer": None,
                "musicType": None,
            }

    def test_ticket_collection_in_app(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.IN_APP,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.get(f"/public/offers/v1/events/{event_offer.id}")

            assert response.status_code == 200
            assert response.json["hasTicket"] == True

    def test_ticket_collection_no_ticket(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue()
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
            withdrawalType=offers_models.WithdrawalTypeEnum.NO_TICKET,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}"
            )

            assert response.status_code == 200
            assert response.json["hasTicket"] == False

    def test_404_inactive_venue_provider(self, client):
        venue, _ = utils.create_offerer_provider_linked_to_venue(is_venue_provider_active=False)
        event_offer = offers_factories.EventOfferFactory(
            venue=venue,
        )
        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(4):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/public/offers/v1/events/{event_offer.id}"
            )

            assert response.status_code == 404
