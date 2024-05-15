from operator import itemgetter

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories


@pytest.mark.usefixtures("db_session")
class CollectiveOffersPublicGetOfferTest:
    def test_get_offer(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()

        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        national_program = educational_factories.NationalProgramFactory()
        domain = educational_factories.EducationalDomainFactory()
        institution = educational_factories.EducationalInstitutionFactory(institutionId="UAI123")
        booking = educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__domains=[domain],
            collectiveStock__collectiveOffer__provider=venue_provider.provider,
            collectiveStock__collectiveOffer__imageCredit="Pouet",
            collectiveStock__collectiveOffer__imageCrop={"data": 2},
            collectiveStock__collectiveOffer__institution=institution,
            collectiveStock__collectiveOffer__nationalProgram=national_program,
            collectiveStock__collectiveOffer__formats=["CONCERT"],
        )
        offer = booking.collectiveStock.collectiveOffer
        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective/offers/{offer.id}"
        )

        # Then
        assert response.status_code == 200
        assert sort_response_offer_json(response.json) == expected_serialized_offer(offer)

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
        offer = educational_factories.CollectiveStockFactory().collectiveOffer
        response = client.get(f"/v2/collective/offers/{offer.id}")
        assert response.status_code == 401

    def test_user_no_access_to_user(self, client):
        # Given
        venue_provider = provider_factories.VenueProviderFactory()
        offerers_factories.ApiKeyFactory(provider=venue_provider.provider)

        venue_provider2 = provider_factories.VenueProviderFactory()
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider2.provider,
        )
        offer = stock.collectiveOffer

        # When
        response = client.with_explicit_token(offerers_factories.DEFAULT_CLEAR_API_KEY).get(
            f"/v2/collective/offers/{offer.id}"
        )

        # Then
        assert response.status_code == 403


def sort_response_offer_json(response_offer):
    booking_emails = response_offer["bookingEmails"]
    if booking_emails:
        response_offer["bookingEmails"] = sorted(booking_emails)

    bookings = response_offer["bookings"]
    if bookings:
        response_offer["bookings"] = sorted(bookings, key=itemgetter("id"))

    return response_offer


def expected_serialized_offer(offer):
    bookings = [
        {
            "id": booking.id,
            "status": booking.status.value,
            "confirmationDate": booking.confirmationDate.isoformat() if booking.confirmationDate else None,
            "cancellationLimitDate": (
                booking.cancellationLimitDate.isoformat() if booking.cancellationLimitDate else None
            ),
            "reimbursementDate": booking.reimbursementDate.isoformat() if booking.reimbursementDate else None,
            "dateUsed": booking.dateUsed.isoformat() if booking.dateUsed else None,
            "dateCreated": booking.dateCreated.isoformat() if booking.dateCreated else None,
        }
        for booking in offer.collectiveStock.collectiveBookings
    ]
    bookings = sorted(bookings, key=itemgetter("id"))

    return {
        "id": offer.id,
        "name": offer.name,
        "description": offer.description,
        "venueId": offer.venue.id,
        "audioDisabilityCompliant": offer.audioDisabilityCompliant,
        "startDatetime": offer.collectiveStock.startDatetime.replace(microsecond=0).isoformat(),
        "endDatetime": offer.collectiveStock.endDatetime.replace(microsecond=0).isoformat(),
        "bookingLimitDatetime": offer.collectiveStock.bookingLimitDatetime.replace(microsecond=0).isoformat(),
        "bookingEmails": sorted(offer.bookingEmails),
        "contactEmail": offer.contactEmail,
        "contactPhone": offer.contactPhone,
        "dateCreated": offer.dateCreated.replace(microsecond=0).isoformat(),
        "domains": [domain.id for domain in offer.domains],
        "durationMinutes": offer.durationMinutes,
        "educationalInstitution": offer.institution.institutionId if offer.institution else None,
        "educationalInstitutionId": offer.institutionId,
        "educationalPriceDetail": offer.collectiveStock.priceDetail,
        "interventionArea": offer.interventionArea,
        "isActive": offer.isActive,
        "isSoldOut": offer.isSoldOut,
        "numberOfTickets": offer.collectiveStock.numberOfTickets,
        "status": offer.status.name,
        "students": [student.name for student in offer.students],
        "subcategoryId": offer.subcategoryId,
        "totalPrice": float(offer.collectiveStock.price),
        "hasBookingLimitDatetimesPassed": offer.hasBookingLimitDatetimesPassed,
        "mentalDisabilityCompliant": offer.mentalDisabilityCompliant,
        "motorDisabilityCompliant": offer.motorDisabilityCompliant,
        "visualDisabilityCompliant": offer.visualDisabilityCompliant,
        "offerVenue": {
            "addressType": offer.offerVenue["addressType"],
            "otherAddress": offer.offerVenue["otherAddress"],
            "venueId": offer.offerVenue["venueId"],
        },
        "imageCredit": offer.imageCredit,
        "imageUrl": offer.imageUrl,
        "nationalProgram": {"id": offer.nationalProgram.id, "name": offer.nationalProgram.name},
        "bookings": bookings,
        "formats": [fmt.value for fmt in offer.formats] if offer.formats else None,
    }
