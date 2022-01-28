import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.educational.factories import EducationalDepositFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.offers.utils import offer_app_link
from pcapi.core.testing import assert_num_queries
from pcapi.utils.date import format_into_utc_date

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_educational_institution(self, app) -> None:
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=2000,
            isFinal=True,
        )
        EducationalInstitutionFactory()
        booking = EducationalBookingFactory(
            educationalBooking__educationalRedactor=redactor,
            educationalBooking__educationalYear=educational_year,
            educationalBooking__educationalInstitution=educational_institution,
        )
        other_educational_year = EducationalYearFactory(adageId="toto")
        other_educational_institution = EducationalInstitutionFactory(institutionId="tata")
        EducationalBookingFactory(educationalBooking__educationalYear=other_educational_year)
        EducationalBookingFactory(educationalBooking__educationalInstitution=other_educational_institution)
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=other_educational_year,
            amount=2000,
            isFinal=False,
        )
        EducationalDepositFactory(
            educationalInstitution=other_educational_institution,
            educationalYear=educational_year,
            amount=2000,
            isFinal=False,
        )

        client = TestClient(app.test_client()).with_eac_token()
        response = client.get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}"
        )

        assert response.status_code == 200

        stock = booking.stock
        offer = stock.offer
        venue = offer.venue
        educational_booking = booking.educationalBooking
        assert response.json == {
            "credit": 2000,
            "isFinal": True,
            "prebookings": [
                {
                    "address": f"{venue.address}, {venue.postalCode} {venue.city}",
                    "accessibility": "Non accessible",
                    "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
                    "cancellationDate": None,
                    "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
                    "city": venue.city,
                    "confirmationDate": format_into_utc_date(educational_booking.confirmationDate)
                    if educational_booking.confirmationDate
                    else None,
                    "confirmationLimitDate": format_into_utc_date(educational_booking.confirmationLimitDate),
                    "contact": {"email": None, "phone": None},
                    "coordinates": {
                        "latitude": float(venue.latitude),
                        "longitude": float(venue.longitude),
                    },
                    "creationDate": format_into_utc_date(booking.dateCreated),
                    "description": offer.description,
                    "durationMinutes": offer.durationMinutes,
                    "expirationDate": booking.expirationDate,
                    "id": educational_booking.id,
                    "isDigital": offer.isDigital,
                    "venueName": venue.name,
                    "name": offer.name,
                    "numberOfTickets": 30,
                    "participants": [],
                    "priceDetail": stock.educationalPriceDetail,
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
                    "subcategoryLabel": "Séance de cinéma",
                    "venueTimezone": venue.timezone,
                    "totalAmount": booking.amount * booking.quantity,
                    "url": offer_app_link(offer),
                    "withdrawalDetails": offer.withdrawalDetails,
                }
            ],
        }

    def test_get_educational_institution_num_queries(self, app) -> None:
        redactor = EducationalRedactorFactory()
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=200000,
            isFinal=True,
        )
        EducationalInstitutionFactory()
        EducationalBookingFactory.create_batch(
            10,
            educationalBooking__educationalRedactor=redactor,
            educationalBooking__educationalYear=educational_year,
            educationalBooking__educationalInstitution=educational_institution,
        )
        other_educational_year = EducationalYearFactory(adageId="toto")
        other_educational_institution = EducationalInstitutionFactory(institutionId="tata")
        EducationalBookingFactory(educationalBooking__educationalYear=other_educational_year)
        EducationalBookingFactory(educationalBooking__educationalInstitution=other_educational_institution)
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=other_educational_year,
            amount=2000,
            isFinal=False,
        )
        EducationalDepositFactory(
            educationalInstitution=other_educational_institution,
            educationalYear=educational_year,
            amount=2000,
            isFinal=False,
        )

        client = TestClient(app.test_client()).with_eac_token()
        adage_id = educational_year.adageId
        institution_id = educational_institution.institutionId

        n_queries = 0
        n_queries += 1  # Check for educational institution
        n_queries += 1  # Get needed data
        n_queries += 1  # Get deposit

        with assert_num_queries(n_queries):
            client.get(f"/adage/v1/years/{adage_id}/educational_institution/{institution_id}")

    def test_get_educational_institution_without_deposit(self, app) -> None:
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()

        client = TestClient(app.test_client()).with_eac_token()
        response = client.get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}"
        )

        assert response.status_code == 200

        assert response.json == {
            "credit": 0,
            "isFinal": False,
            "prebookings": [],
        }


class Returns404Test:
    def test_get_educational_institution_not_found(self, app, db_session) -> None:
        educational_year = EducationalYearFactory()
        EducationalInstitutionFactory()

        client = TestClient(app.test_client()).with_eac_token()
        response = client.get(f"/adage/v1/years/{educational_year.adageId}/educational_institution/UNKNOWN")

        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_INSTITUTION_NOT_FOUND"}
