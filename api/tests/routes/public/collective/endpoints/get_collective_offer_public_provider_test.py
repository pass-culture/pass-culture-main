from operator import itemgetter

from freezegun import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories


@pytest.mark.usefixtures("db_session")
@freeze_time("2022-05-01 15:00:00")
class CollectiveOffersPublicGetOfferTest:
    def test_get_offer(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        domain = educational_factories.EducationalDomainFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="UAI123")
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__domains=[domain],
            collectiveStock__collectiveOffer__provider=venue_provider.provider,
            collectiveStock__collectiveOffer__imageCredit="Pouet",
            collectiveStock__collectiveOffer__imageCrop={"data": 2},
            collectiveStock__collectiveOffer__institution=institution,
        )
        offer = booking.collectiveStock.collectiveOffer
        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective/offers/{offer.id}"
        )

        # Then
        assert response.status_code == 200

        bookings = [
            {
                "id": booking.id,
                "status": booking.status.value,
                "confirmationDate": booking.confirmationDate.isoformat() if booking.confirmationDate else None,
                "cancellationLimitDate": booking.cancellationLimitDate.isoformat()
                if booking.cancellationLimitDate
                else None,
                "reimbursementDate": booking.reimbursementDate.isoformat() if booking.reimbursementDate else None,
                "dateUsed": booking.dateUsed.isoformat() if booking.dateUsed else None,
                "dateCreated": booking.dateCreated.isoformat() if booking.dateCreated else None,
            }
            for booking in offer.collectiveStock.collectiveBookings
        ]
        bookings = sorted(bookings, key=itemgetter("id"))

        assert response.json["id"] == offer.id
        assert response.json["name"] == offer.name
        assert response.json["description"] == offer.description
        assert response.json["venueId"] == offer.venue.id
        assert response.json["audioDisabilityCompliant"] == False
        assert response.json["beginningDatetime"] == "2022-05-02T15:00:00"
        assert sorted(response.json["bookingEmails"]) == sorted(
            [
                "collectiveofferfactory+booking@example.com",
                "collectiveofferfactory+booking@example2.com",
            ]
        )
        assert response.json["bookingLimitDatetime"] == "2022-05-02T14:00:00"
        assert response.json["contactEmail"] == "collectiveofferfactory+contact@example.com"
        assert response.json["contactPhone"] == "+33199006328"
        assert response.json["dateCreated"] == "2022-04-26T15:00:00"
        assert response.json["domains"] == [domain.id]
        assert response.json["durationMinutes"] == None
        assert response.json["educationalInstitution"] == "UAI123"
        assert response.json["educationalInstitutionId"] == institution.id
        assert response.json["educationalPriceDetail"] == None
        assert response.json["interventionArea"] == ["93", "94", "95"]
        assert response.json["isActive"]
        assert response.json["isSoldOut"]
        assert response.json["numberOfTickets"] == 25
        assert response.json["status"] == "SOLD_OUT"
        assert response.json["students"] == ["GENERAL2"]
        assert response.json["subcategoryId"] == offer.subcategoryId
        assert response.json["totalPrice"] == float(offer.collectiveStock.price)
        assert response.json["hasBookingLimitDatetimesPassed"] == False
        assert response.json["mentalDisabilityCompliant"] == False
        assert response.json["motorDisabilityCompliant"] == False
        assert response.json["visualDisabilityCompliant"] == False
        assert response.json["offerVenue"] == {
            "addressType": "other",
            "otherAddress": "1 rue des polissons, Paris 75017",
            "venueId": None,
        }
        assert response.json["imageCredit"] == offer.imageCredit
        assert response.json["imageUrl"] == offer.imageUrl
        assert sorted(response.json["bookings"], key=itemgetter("id")) == bookings

    def test_offer_does_not_exists(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get("/v2/collective/offers/-1")

        # Then
        assert response.status_code == 404

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
