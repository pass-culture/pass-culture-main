from operator import itemgetter

import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.providers import factories as provider_factories
from pcapi.core.testing import assert_num_queries

from tests.routes.public.helpers import PublicAPIEndpointBaseHelper


@pytest.mark.usefixtures("db_session")
class CollectiveOffersPublicGetOfferTest(PublicAPIEndpointBaseHelper):
    endpoint_url = "/v2/collective/offers/{offer_id}"
    endpoint_method = "get"
    default_path_params = {"offer_id": 1}

    num_queries = 1  # select api_key, offerer and provider
    num_queries += 1  # select collective_offer and collective_stock
    num_queries_error = num_queries + 1  # rollback

    def test_get_offer(self):
        plain_api_key, provider = self.setup_provider()
        venue_provider = provider_factories.VenueProviderFactory(provider=provider)

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
        offer_id = offer.id

        with assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, {"offer_id": offer_id})
            assert response.status_code == 200

        assert sort_response_offer_json(response.json) == expected_serialized_offer(offer)

    def test_get_offer_no_program_no_booking(self):
        plain_api_key, provider = self.setup_provider()
        venue_provider = provider_factories.VenueProviderFactory(provider=provider)
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
            collectiveOffer__nationalProgram=None,
        )
        offer_id = stock.collectiveOffer.id

        with assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, {"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json["nationalProgram"] is None
        assert response.json["bookings"] == []

    def test_get_offer_on_school_location(self, client):
        plain_api_key, provider = self.setup_provider()
        venue_provider = provider_factories.VenueProviderFactory(provider=provider)

        offer = educational_factories.CollectiveOfferOnSchoolLocationFactory(
            provider=venue_provider.provider,
        )
        offer_id = offer.id

        with assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, {"offer_id": offer_id})
            assert response.status_code == 200

        assert "location" in response.json
        assert response.json["location"] == {"type": "SCHOOL"}

    def test_get_offer_on_address_venue_location(self):
        plain_api_key, provider = self.setup_provider()
        venue_provider = provider_factories.VenueProviderFactory(provider=provider)
        venue = offerers_factories.VenueFactory()

        offer = educational_factories.CollectiveOfferOnAddressVenueLocationFactory(
            provider=venue_provider.provider,
            venue=venue,
        )
        offer_id = offer.id

        with assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, {"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json["location"] == {"type": "ADDRESS", "isVenueAddress": True}

    def test_get_offer_on_other_address_location(self):
        plain_api_key, provider = self.setup_provider()
        venue_provider = provider_factories.VenueProviderFactory(provider=provider)
        venue = offerers_factories.VenueFactory()
        offerer_address = offerers_factories.OffererAddressFactory(offerer=venue.managingOfferer)

        offer = educational_factories.CollectiveOfferOnOtherAddressLocationFactory(
            provider=venue_provider.provider,
            venue=venue,
            offererAddress=offerer_address,
        )
        offer_id = offer.id
        oa = offerer_address

        with assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, {"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json["location"] == {
            "type": "ADDRESS",
            "addressLabel": oa.label,
            "addressId": oa.addressId,
            "isVenueAddress": False,
        }

    def test_get_offer_on_to_be_defined_location(self, client):
        plain_api_key, provider = self.setup_provider()
        venue_provider = provider_factories.VenueProviderFactory(provider=provider)

        offer = educational_factories.CollectiveOfferOnToBeDefinedLocationFactory(
            provider=venue_provider.provider,
        )
        offer_id = offer.id

        with assert_num_queries(self.num_queries):
            response = self.make_request(plain_api_key, {"offer_id": offer_id})
            assert response.status_code == 200

        assert response.json["location"] == {
            "type": "TO_BE_DEFINED",
            "comment": "In space",
        }

    def test_offer_does_not_exists(self):
        plain_api_key, provider = self.setup_provider()
        provider_factories.VenueProviderFactory(provider=provider)

        with assert_num_queries(self.num_queries_error):
            response = self.make_request(plain_api_key, {"offer_id": 25})
            assert response.status_code == 404

    def test_offer_without_stock(self):
        plain_api_key, provider = self.setup_provider()
        venue_provider = provider_factories.VenueProviderFactory(provider=provider)
        offerers_factories.VenueFactory(venueProviders=[venue_provider])

        educational_factories.EducationalDomainFactory()
        educational_factories.EducationalInstitutionFactory(institutionId="UAI123")
        educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider.provider,
        )
        offer = educational_factories.CollectiveOfferFactory()
        offer_id = offer.id

        with assert_num_queries(self.num_queries_error):
            response = self.make_request(plain_api_key, {"offer_id": offer_id})
            assert response.status_code == 404

    def test_user_no_access_to_user(self):
        plain_api_key, provider = self.setup_provider()
        provider_factories.VenueProviderFactory(provider=provider)

        venue_provider2 = provider_factories.VenueProviderFactory()
        stock = educational_factories.CollectiveStockFactory(
            collectiveOffer__provider=venue_provider2.provider,
        )
        offer_id = stock.collectiveOffer.id

        with assert_num_queries(self.num_queries_error):
            response = self.make_request(plain_api_key, {"offer_id": offer_id})
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
        "offerStatus": offer.displayedStatus.value,
        "students": [student.name for student in offer.students],
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
        "formats": [fmt.value for fmt in offer.formats],
        "location": {"type": "TO_BE_DEFINED", "comment": None},
    }
