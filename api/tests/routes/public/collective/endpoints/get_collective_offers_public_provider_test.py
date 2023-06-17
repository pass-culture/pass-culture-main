from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories
from pcapi.core.testing import override_features
from pcapi.models.offer_mixin import OfferValidationStatus


@pytest.mark.usefixtures("db_session")
@freeze_time("2022-05-01 15:00:00")
class CollectiveOffersPublicGetOfferTest:
    @override_features(ENABLE_PROVIDER_AUTHENTIFICATION=True)
    def test_get_offers(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock1 = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer1 = stock1.collectiveOffer
        stock2 = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer2 = stock2.collectiveOffer
        stock3 = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer3 = stock3.collectiveOffer
        stock4 = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer4 = stock4.collectiveOffer
        stock5 = educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        offer5 = stock5.collectiveOffer

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/v2/collective/offers/")

        # Then
        assert response.status_code == 200

        assert response.json == [
            {
                "id": offer1.id,
                "venueId": offer1.venueId,
                "beginningDatetime": "2022-05-02T15:00:00",
                "status": offer1.status.name,
            },
            {
                "id": offer2.id,
                "venueId": offer2.venueId,
                "beginningDatetime": "2022-05-02T15:00:00",
                "status": offer2.status.name,
            },
            {
                "id": offer3.id,
                "venueId": offer3.venueId,
                "beginningDatetime": "2022-05-02T15:00:00",
                "status": offer3.status.name,
            },
            {
                "id": offer4.id,
                "venueId": offer4.venueId,
                "beginningDatetime": "2022-05-02T15:00:00",
                "status": offer4.status.name,
            },
            {
                "id": offer5.id,
                "venueId": offer5.venueId,
                "beginningDatetime": "2022-05-02T15:00:00",
                "status": offer5.status.name,
            },
        ]

    @override_features(ENABLE_PROVIDER_AUTHENTIFICATION=True)
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
                "status": "ACTIVE",
            },
            {
                "id": offer2.id,
                "venueId": offer2.venueId,
                "beginningDatetime": "2043-05-02T15:00:00",
                "status": "ACTIVE",
            },
        ]

    @override_features(ENABLE_PROVIDER_AUTHENTIFICATION=True)
    def test_no_offers(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/v2/collective/offers/")

        # Then
        assert response.status_code == 200
        assert not response.json

    @override_features(ENABLE_PROVIDER_AUTHENTIFICATION=True)
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
                "beginningDatetime": "2022-05-02T15:00:00",
                "status": offer.status.name,
            },
        ]

    @override_features(ENABLE_PROVIDER_AUTHENTIFICATION=True)
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
                "beginningDatetime": "2022-05-02T15:00:00",
                "status": offer1.status.name,
            },
        ]

    @override_features(ENABLE_PROVIDER_AUTHENTIFICATION=True)
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
                "beginningDatetime": "2022-05-02T15:00:00",
                "status": offer1.status.name,
            },
        ]

    @override_features(ENABLE_PROVIDER_AUTHENTIFICATION=True)
    def test_user_not_logged_in(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        educational_factories.CollectiveStockFactory(collectiveOffer__provider=venue_provider.provider)
        # When
        response = client.get("/v2/collective/offers/")

        # Then
        assert response.status_code == 401
