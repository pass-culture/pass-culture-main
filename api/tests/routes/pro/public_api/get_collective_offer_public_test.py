from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories


@pytest.mark.usefixtures("db_session")
@freeze_time("2022-05-01 15:00:00")
class CollectiveOffersPublicGetOfferTest:
    def test_get_offer(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer)
        offer = stock.collectiveOffer
        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective-offers/{offer.id}"
        )

        # Then
        assert response.status_code == 200

        assert response.json == {
            "id": offer.id,
            "name": offer.name,
            "description": offer.description,
            "venueId": offer.venue.id,
            "audioDisabilityCompliant": False,
            "beginningDatetime": "2022-05-02T15:00:00",
            "bookingEmail": "collectiveofferfactory+booking@example.com",
            "bookingLimitDatetime": "2022-05-02T14:00:00",
            "contactEmail": "collectiveofferfactory+contact@example.com",
            "contactPhone": "+33199006328",
            "dateCreated": "2022-04-26T15:00:00",
            "domains": [],
            "durationMinutes": None,
            "educationalInstitution": None,
            "educationalPriceDetail": None,
            "interventionArea": ["93", "94", "95"],
            "isActive": True,
            "isSoldOut": False,
            "numberOfTickets": 25,
            "status": "ACTIVE",
            "students": ["GENERAL2"],
            "subcategoryId": offer.subcategoryId,
            "totalPrice": 10000,
            "hasBookingLimitDatetimesPassed": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {"addressType": "other", "otherAddress": "1 rue des polissons, Paris 75017", "venueId": None},
        }

    def test_offer_does_not_exists(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer)
        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/v2/collective-offers/-1")

        # Then
        assert response.status_code == 404

    def test_offer_without_stock(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue__managingOfferer=offerer)
        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective-offers/{offer.id}"
        )

        # Then
        assert response.status_code == 404

    def test_user_not_logged_in(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer)
        offer = stock.collectiveOffer
        # When
        response = client.get(f"/v2/collective-offers/{offer.id}")

        # Then
        assert response.status_code == 401

    def test_user_no_access_to_user(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.ApiKeyFactory(offerer=offerer)
        offerer2 = offerers_factories.OffererFactory()
        stock = educational_factories.CollectiveStockFactory(collectiveOffer__venue__managingOfferer=offerer2)
        offer = stock.collectiveOffer
        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective-offers/{offer.id}"
        )

        # Then
        assert response.status_code == 403
