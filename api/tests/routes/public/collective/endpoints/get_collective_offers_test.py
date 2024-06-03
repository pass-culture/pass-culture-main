from datetime import datetime

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories
from pcapi.core.testing import assert_num_queries
from pcapi.models.offer_mixin import OfferValidationStatus


@pytest.mark.usefixtures("db_session")
class CollectiveOffersPublicGetOfferTest:
    def test_get_offers(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock1 = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer1 = stock1.collectiveOffer

        offer2 = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__provider=venue_provider.provider
        ).collectiveStock.collectiveOffer
        booking2 = offer2.collectiveStock.collectiveBookings[0]

        # When
        # 1. fetch api key
        # 2. fetch data
        # 3. fetch FF
        with assert_num_queries(3):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                "/v2/collective/offers/"
            )

        # Then
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
        # Given
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

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            "/v2/collective/offers/?status=ACTIVE"
        )

        # Then
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
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/v2/collective/offers/")

        # Then
        assert response.status_code == 200
        assert not response.json

    def test_offer_without_stock(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer = stock.collectiveOffer

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/v2/collective/offers/")

        # Then
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
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock1 = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer1 = stock1.collectiveOffer

        venue_provider2 = provider_factories.VenueProviderFactory()
        educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider2.provider)

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/v2/collective/offers/")

        # Then
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
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock1 = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer1 = stock1.collectiveOffer
        educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__validation=OfferValidationStatus.DRAFT,
        )

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/v2/collective/offers/")

        # Then
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

    def test_user_not_logged_in(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        # When
        response = client.get("/v2/collective/offers/")

        # Then
        assert response.status_code == 401

    def test_user_did_not_create_offer_using_the_api(self, client):
        """Ensure that a user cannot fetch an offer that he did not
        created with the API"""
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = educational_factories.CollectiveStockFactory().collectiveOffer

        api_client = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY)
        response = api_client.get(f"/v2/collective/offers/{offer.id}")

        assert response.status_code == 403

    def test_offer_venue_has_an_empty_string_venue_id(self, client):
        # TODO(jeremieb): remove this test once there is no empty
        # string stored as a venueId
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        offer = educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__offerVenue={"venueId": "", "addressType": "offererVenue", "otherAddress": ""},
        ).collectiveOffer

        # 1. fetch api key
        # 2. fetch data
        # 3. fetch FF
        with assert_num_queries(3):
            response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
                f"/v2/collective/offers/{offer.id}"
            )

        assert response.status_code == 200
        assert response.json["offerVenue"] == {
            "venueId": None,
            "addressType": "offererVenue",
            "otherAddress": None,
        }
