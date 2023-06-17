from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories
from pcapi.core.testing import override_features


@pytest.mark.usefixtures("db_session")
@freeze_time("2022-05-01 15:00:00")
class CollectiveOffersPublicGetOfferTest:
    @override_features(ENABLE_PROVIDER_AUTHENTIFICATION=True)
    def test_get_offer(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        domain = educational_factories.EducationalDomainFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="UAI123")
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__domains=[domain],
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__imageCredit="Pouet",
            collectiveOffer__imageCrop={"data": 2},
            collectiveOffer__institution=institution,
        )
        offer = stock.collectiveOffer
        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective/offers/{offer.id}"
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
            "bookingEmails": [
                "collectiveofferfactory+booking@example.com",
                "collectiveofferfactory+booking@example2.com",
            ],
            "bookingLimitDatetime": "2022-05-02T14:00:00",
            "contactEmail": "collectiveofferfactory+contact@example.com",
            "contactPhone": "+33199006328",
            "dateCreated": "2022-04-26T15:00:00",
            "domains": [domain.id],
            "durationMinutes": None,
            "educationalInstitution": "UAI123",
            "educationalInstitutionId": institution.id,
            "educationalPriceDetail": None,
            "interventionArea": ["93", "94", "95"],
            "isActive": True,
            "isSoldOut": False,
            "numberOfTickets": 25,
            "status": "ACTIVE",
            "students": ["GENERAL2"],
            "subcategoryId": offer.subcategoryId,
            "totalPrice": float(offer.collectiveStock.price),
            "hasBookingLimitDatetimesPassed": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "offerVenue": {"addressType": "other", "otherAddress": "1 rue des polissons, Paris 75017", "venueId": None},
            "imageCredit": offer.imageCredit,
            "imageUrl": offer.imageUrl,
        }

    @override_features(ENABLE_PROVIDER_AUTHENTIFICATION=True)
    def test_offer_does_not_exists(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/v2/collective/offers/-1")

        # Then
        assert response.status_code == 404

    @override_features(ENABLE_PROVIDER_AUTHENTIFICATION=True)
    def test_offer_without_stock(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.VenueFactory(venueProviders=[venue_provider])

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        educational_factories.EducationalDomainFactory()
        educational_factories.EducationalInstitutionFactory(institutionId="UAI123")
        educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
        )
        offer = educational_factories.CollectiveOfferFactory()

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective/offers/{offer.id}"
        )

        # Then
        assert response.status_code == 404

    @override_features(ENABLE_PROVIDER_AUTHENTIFICATION=True)
    def test_user_not_logged_in(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
        )
        offer = stock.collectiveOffer

        # When
        response = client.get(f"/v2/collective/offers/{offer.id}")

        # Then
        assert response.status_code == 401

    @override_features(ENABLE_PROVIDER_AUTHENTIFICATION=True)
    def test_user_no_access_to_user(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        domain = educational_factories.EducationalDomainFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="UAI123")

        venue_provider2 = provider_factories.VenueProviderFactory()
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__domains=[domain],
            collectiveOffer__provider=venue_provider2.provider,
            collectiveOffer__imageCredit="Pouet",
            collectiveOffer__imageCrop={"data": 2},
            collectiveOffer__institution=institution,
        )
        offer = stock.collectiveOffer

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective/offers/{offer.id}"
        )

        # Then
        assert response.status_code == 403
