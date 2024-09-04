from datetime import datetime

import pytest

from pcapi.core import testing
from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories
from pcapi.models.offer_mixin import OfferValidationStatus

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CollectiveOffersPublicGetOfferTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/offers/"
    endpoint_method = "get"

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select features
    num_queries += 1  # select offers and bookings

    def test_get_offers(self, client):
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock1 = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer1 = stock1.collectiveOffer

        offer2 = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__provider=venue_provider.provider
        ).collectiveStock.collectiveOffer
        booking2 = offer2.collectiveStock.collectiveBookings[0]

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/v2/collective/offers/"
            )
            assert response.status_code == 200

        assert response.json == [
            {
                "id": offer1.id,
                "venueId": offer1.venueId,
                "beginningDatetime": stock1.beginningDatetime.isoformat(timespec="seconds"),
                "startDatetime": stock1.startDatetime.isoformat(timespec="seconds"),
                "endDatetime": stock1.endDatetime.isoformat(timespec="seconds"),
                "status": offer1.status.name,
                "bookings": [],
            },
            {
                "id": offer2.id,
                "venueId": offer2.venueId,
                "beginningDatetime": offer2.collectiveStock.beginningDatetime.isoformat(timespec="seconds"),
                "startDatetime": offer2.collectiveStock.startDatetime.isoformat(timespec="seconds"),
                "endDatetime": offer2.collectiveStock.endDatetime.isoformat(timespec="seconds"),
                "status": offer2.status.name,
                "bookings": [
                    {
                        "id": booking2.id,
                        "status": booking2.status.value,
                        "confirmationDate": (
                            booking2.confirmationDate.isoformat() if booking2.confirmationDate else None
                        ),
                        "cancellationLimitDate": (
                            booking2.cancellationLimitDate.isoformat() if booking2.cancellationLimitDate else None
                        ),
                        "reimbursementDate": (
                            booking2.reimbursementDate.isoformat() if booking2.reimbursementDate else None
                        ),
                        "dateUsed": booking2.dateUsed.isoformat() if booking2.dateUsed else None,
                        "dateCreated": booking2.dateCreated.isoformat() if booking2.dateCreated else None,
                    }
                ],
            },
        ]

    def test_get_offers_filter_by_status(self, client):
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock1 = educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            beginningDatetime=datetime(2043, 5, 2, 15),
        )
        offer1 = stock1.collectiveOffer
        stock2 = educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            beginningDatetime=datetime(2043, 5, 2, 15),
        )
        offer2 = stock2.collectiveOffer

        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/v2/collective/offers/?status=ACTIVE"
            )
            assert response.status_code == 200

        assert response.json == [
            {
                "id": offer1.id,
                "venueId": offer1.venueId,
                "beginningDatetime": "2043-05-02T15:00:00",
                "startDatetime": "2043-05-02T15:00:00",
                "endDatetime": "2043-05-02T15:00:00",
                "status": "ACTIVE",
                "bookings": [],
            },
            {
                "id": offer2.id,
                "venueId": offer2.venueId,
                "beginningDatetime": "2043-05-02T15:00:00",
                "startDatetime": "2043-05-02T15:00:00",
                "endDatetime": "2043-05-02T15:00:00",
                "status": "ACTIVE",
                "bookings": [],
            },
        ]

    def test_no_offers(self, client):
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(self.num_queries):
            response = client.get("/v2/collective/offers/")
            assert response.status_code == 200

        assert not response.json

    def test_offer_without_stock(self, client):
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer = stock.collectiveOffer

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(self.num_queries):
            response = client.get("/v2/collective/offers/")
            assert response.status_code == 200

        assert response.json == [
            {
                "id": offer.id,
                "venueId": offer.venueId,
                "beginningDatetime": stock.beginningDatetime.isoformat(timespec="seconds"),
                "startDatetime": stock.startDatetime.isoformat(timespec="seconds"),
                "endDatetime": stock.endDatetime.isoformat(timespec="seconds"),
                "status": offer.status.name,
                "bookings": [],
            },
        ]

    def test_other_offerer_offers_not_visible(self, client):
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock1 = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer1 = stock1.collectiveOffer

        venue_provider2 = provider_factories.VenueProviderFactory()
        educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider2.provider)

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(self.num_queries):
            response = client.get("/v2/collective/offers/")
            assert response.status_code == 200

        assert response.json == [
            {
                "id": offer1.id,
                "venueId": offer1.venueId,
                "beginningDatetime": stock1.beginningDatetime.isoformat(timespec="seconds"),
                "startDatetime": stock1.startDatetime.isoformat(timespec="seconds"),
                "endDatetime": stock1.endDatetime.isoformat(timespec="seconds"),
                "status": offer1.status.name,
                "bookings": [],
            },
        ]

    def test_draft_offers_not_visible(self, client):
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock1 = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer1 = stock1.collectiveOffer
        educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__validation=OfferValidationStatus.DRAFT,
        )

        client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(self.num_queries):
            response = client.get("/v2/collective/offers/")
            assert response.status_code == 200

        assert response.json == [
            {
                "id": offer1.id,
                "venueId": offer1.venueId,
                "beginningDatetime": stock1.beginningDatetime.isoformat(timespec="seconds"),
                "startDatetime": stock1.startDatetime.isoformat(timespec="seconds"),
                "endDatetime": stock1.endDatetime.isoformat(timespec="seconds"),
                "status": offer1.status.name,
                "bookings": [],
            },
        ]

    def test_user_did_not_create_offer_using_the_api(self, client):
        """Ensure that a user cannot fetch an offer that he did not
        created with the API"""
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer_id = educational_factories.CollectiveStockFactory().collectiveOffer.id

        api_client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        with testing.assert_num_queries(self.num_queries):
            response = api_client.get(f"/v2/collective/offers/{offer_id}")
            assert response.status_code == 403

    def test_offer_venue_has_an_empty_string_venue_id(self, client):
        # TODO(jeremieb): remove this test once there is no empty
        # string stored as a venueId
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__offerVenue={"venueId": "", "addressType": "offererVenue", "otherAddress": ""},
        )
        offer_id = stock.collectiveOffer.id
        with testing.assert_num_queries(self.num_queries):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/v2/collective/offers/{offer_id}"
            )
            assert response.status_code == 200

        assert response.json["offerVenue"] == {
            "venueId": None,
            "addressType": "offererVenue",
            "otherAddress": None,
        }
