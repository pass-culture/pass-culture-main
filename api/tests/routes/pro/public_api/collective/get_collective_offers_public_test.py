from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.models.offer_mixin import OfferValidationStatus


@pytest.mark.usefixtures("db_session")
@freeze_time("2022-05-01 15:00:00")
class CollectiveOffersPublicGetOfferTest:
    def test_get_offers(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        stock1 = educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer)
        offer1 = stock1.collectiveOffer
        stock2 = educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer)
        offer2 = stock2.collectiveOffer
        stock3 = educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer)
        offer3 = stock3.collectiveOffer
        stock4 = educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer)
        offer4 = stock4.collectiveOffer
        stock5 = educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer)
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

    def test_no_offers(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/v2/collective/offers/")

        # Then
        assert response.status_code == 200
        assert response.json == []

    def test_offer_without_stock(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer)
        offer = stock.collectiveOffer
        educational_factories.CollectiveOfferFactory(venue__managingOfferer=offerer)
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

    def test_other_offerer_offers_not_visible(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer)
        offer = stock.collectiveOffer
        offerer2 = offerers_factories.OffererFactory()
        educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer2)
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

    def test_draft_offers_not_visible(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer)
        offer = stock.collectiveOffer
        educational_factories.CollectiveStockFactory(
            collectiveOffer__venue__managingOfferer=offerer,
            collectiveOffer__validation=OfferValidationStatus.DRAFT,
        )

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

    def test_user_not_logged_in(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer)
        # When
        response = client.get("/v2/collective/offers/")

        # Then
        assert response.status_code == 401
