import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.routes.native.v1.serialization.offers import get_serialized_offer_category
from pcapi.utils.human_ids import humanize
from pcapi.utils.urls import get_webapp_url

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_prebookings_without_query_params(self, app) -> None:
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        educationalYear = EducationalYearFactory()
        educationalInstitution = EducationalInstitutionFactory()
        booking = EducationalBookingFactory(
            educationalBooking__educationalYear=educationalYear,
            educationalBooking__educationalInstitution=educationalInstitution,
            educationalBooking__educationalRedactor=redactor,
        )
        other_educational_year = EducationalYearFactory(adageId="toto")
        other_educational_institution = EducationalInstitutionFactory(institutionId="tata")
        EducationalBookingFactory(educationalBooking__educationalYear=other_educational_year)
        EducationalBookingFactory(educationalBooking__educationalInstitution=other_educational_institution)

        client = TestClient(app.test_client()).with_eac_token()
        response = client.get(
            f"/adage/v1/years/{booking.educationalBooking.educationalYear.adageId}/educational_institution/{booking.educationalBooking.educationalInstitution.institutionId}/prebookings"
        )

        assert response.status_code == 200

        stock = booking.stock
        offer = stock.offer
        venue = offer.venue
        educational_booking = booking.educationalBooking
        assert response.json == {
            "prebookings": [
                {
                    "address": venue.address,
                    "beginningDatetime": stock.beginningDatetime.isoformat(),
                    "cancellationDate": None,
                    "cancellationLimitDate": booking.cancellationLimitDate.isoformat(),
                    "category": get_serialized_offer_category(offer),
                    "city": venue.city,
                    "confirmationDate": educational_booking.confirmationDate.isoformat()
                    if educational_booking.confirmationDate
                    else None,
                    "confirmationLimitDate": educational_booking.confirmationLimitDate.isoformat(),
                    "coordinates": {
                        "latitude": float(venue.latitude),
                        "longitude": float(venue.longitude),
                    },
                    "creationDate": booking.dateCreated.isoformat(),
                    "description": offer.description,
                    "durationMinutes": offer.durationMinutes,
                    "expirationDate": booking.expirationDate,
                    "id": educational_booking.id,
                    "image": {"url": offer.image.url, "credit": offer.image.credit} if offer.image else None,
                    "isDigital": offer.isDigital,
                    "venueName": venue.name,
                    "name": offer.name,
                    "postalCode": venue.postalCode,
                    "price": booking.amount,
                    "quantity": booking.quantity,
                    "redactor": {
                        "email": "jean.doux@example.com",
                        "redactorFirstName": "Jean",
                        "redactorLastName": "Doudou",
                        "redactorCivility": "M.",
                    },
                    "UAICode": educational_booking.educationalInstitution.institutionId,
                    "yearId": int(educational_booking.educationalYearId),
                    "status": "CONFIRMED",
                    "venueTimezone": venue.timezone,
                    "totalAmount": booking.amount * booking.quantity,
                    "url": f"{get_webapp_url()}/accueil/details/{humanize(offer.id)}",
                    "withdrawalDetails": offer.withdrawalDetails,
                }
            ],
        }

    def test_get_prebookings_with_query_params(self, app) -> None:
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        another_redactor = EducationalRedactorFactory(
            civility="Mme.",
            firstName="Jeanne",
            lastName="Dodu",
            email="jeanne.dodu@example.com",
        )
        educationalYear = EducationalYearFactory()
        educationalInstitution = EducationalInstitutionFactory()
        booking = EducationalBookingFactory(
            educationalBooking__educationalRedactor=redactor,
            educationalBooking__educationalYear=educationalYear,
            educationalBooking__educationalInstitution=educationalInstitution,
            educationalBooking__status="USED_BY_INSTITUTE",
            status="CONFIRMED",
        )
        EducationalBookingFactory(
            educationalBooking__educationalRedactor=another_redactor,
            educationalBooking__educationalYear=educationalYear,
            educationalBooking__educationalInstitution=educationalInstitution,
            educationalBooking__status="USED_BY_INSTITUTE",
            status="CONFIRMED",
        )
        EducationalBookingFactory(
            educationalBooking__educationalRedactor=redactor,
            educationalBooking__educationalYear=educationalYear,
            educationalBooking__educationalInstitution=educationalInstitution,
            status="PENDING",
        )

        client = TestClient(app.test_client()).with_eac_token()
        response = client.get(
            f"/adage/v1/years/{booking.educationalBooking.educationalYear.adageId}/educational_institution/{booking.educationalBooking.educationalInstitution.institutionId}/prebookings?status=USED_BY_INSTITUTE&redactorEmail={redactor.email}"
        )

        assert response.status_code == 200
        stock = booking.stock
        offer = stock.offer
        venue = offer.venue
        educational_booking = booking.educationalBooking
        assert response.json == {
            "prebookings": [
                {
                    "address": venue.address,
                    "beginningDatetime": stock.beginningDatetime.isoformat(),
                    "cancellationDate": None,
                    "cancellationLimitDate": booking.cancellationLimitDate.isoformat(),
                    "category": get_serialized_offer_category(offer),
                    "city": venue.city,
                    "confirmationDate": educational_booking.confirmationDate.isoformat()
                    if educational_booking.confirmationDate
                    else None,
                    "confirmationLimitDate": educational_booking.confirmationLimitDate.isoformat(),
                    "coordinates": {
                        "latitude": float(venue.latitude),
                        "longitude": float(venue.longitude),
                    },
                    "creationDate": booking.dateCreated.isoformat(),
                    "description": offer.description,
                    "durationMinutes": offer.durationMinutes,
                    "expirationDate": booking.expirationDate,
                    "id": educational_booking.id,
                    "image": {"url": offer.image.url, "credit": offer.image.credit} if offer.image else None,
                    "isDigital": offer.isDigital,
                    "venueName": venue.name,
                    "name": offer.name,
                    "postalCode": venue.postalCode,
                    "price": booking.amount,
                    "quantity": booking.quantity,
                    "redactor": {
                        "email": "jean.doux@example.com",
                        "redactorFirstName": "Jean",
                        "redactorLastName": "Doudou",
                        "redactorCivility": "M.",
                    },
                    "UAICode": educational_booking.educationalInstitution.institutionId,
                    "yearId": int(educational_booking.educationalYearId),
                    "status": "USED_BY_INSTITUTE",
                    "venueTimezone": venue.timezone,
                    "totalAmount": booking.amount * booking.quantity,
                    "url": f"{get_webapp_url()}/accueil/details/{humanize(offer.id)}",
                    "withdrawalDetails": offer.withdrawalDetails,
                }
            ],
        }
