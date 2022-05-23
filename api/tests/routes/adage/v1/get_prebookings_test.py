from typing import Any

import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.factories import PendingEducationalBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.offers.utils import offer_app_link
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_prebookings_without_query_params(self, client: Any) -> None:
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
            stock__offer__description=None,
            stock__offer__extraData={
                "students": [
                    "CAP - 1re ann\u00e9e",
                    "CAP - 2e ann\u00e9e",
                    "Lyc\u00e9e - Seconde",
                    "Lyc\u00e9e - Premi\u00e8re",
                ],
                "offerVenue": {
                    "addressType": "other",
                    "otherAddress": "1 rue des polissons, Paris 75017",
                    "venueId": "",
                },
                "contactEmail": "miss.rond@point.com",
                "contactPhone": "01010100101",
            },
            stock__offer__audioDisabilityCompliant=True,
            stock__offer__visualDisabilityCompliant=True,
        )
        other_educational_year = EducationalYearFactory(adageId="adageId")
        other_educational_institution = EducationalInstitutionFactory(institutionId="institutionId")
        EducationalBookingFactory(educationalBooking__educationalYear=other_educational_year)
        EducationalBookingFactory(educationalBooking__educationalInstitution=other_educational_institution)

        response = client.with_eac_token().get(
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
                    "accessibility": "Auditif, Visuel",
                    "address": "1 rue des polissons, Paris 75017",
                    "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
                    "cancellationDate": None,
                    "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
                    "city": venue.city,
                    "confirmationDate": None,
                    "confirmationLimitDate": format_into_utc_date(educational_booking.confirmationLimitDate),
                    "contact": {"email": "miss.rond@point.com", "phone": "01010100101"},
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
                    "participants": [
                        "CAP - 1re ann\u00e9e",
                        "CAP - 2e ann\u00e9e",
                        "Lyc\u00e9e - Seconde",
                        "Lyc\u00e9e - Premi\u00e8re",
                    ],
                    "priceDetail": "Le prix inclus l'accès à la séance et un atelier une fois la séance terminée. 1000 caractères max.",
                    "postalCode": venue.postalCode,
                    "price": float(booking.amount),
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
                    "subcategoryLabel": offer.subcategory.app_label,
                    "venueTimezone": venue.timezone,
                    "totalAmount": float(booking.amount * booking.quantity),
                    "url": offer_app_link(offer),
                    "withdrawalDetails": offer.withdrawalDetails,
                    "domainIds": [],
                    "domainLabels": [],
                }
            ],
        }

    def test_get_prebookings_with_query_params(self, client: Any) -> None:
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
        EducationalBookingFactory(
            educationalBooking__educationalRedactor=redactor,
            educationalBooking__educationalYear=educationalYear,
            educationalBooking__educationalInstitution=educationalInstitution,
            status="CONFIRMED",
        )
        PendingEducationalBookingFactory(
            educationalBooking__educationalRedactor=another_redactor,
            educationalBooking__educationalYear=educationalYear,
            educationalBooking__educationalInstitution=educationalInstitution,
        )
        booking = PendingEducationalBookingFactory(
            educationalBooking__educationalRedactor=redactor,
            educationalBooking__educationalYear=educationalYear,
            educationalBooking__educationalInstitution=educationalInstitution,
        )

        response = client.with_eac_token().get(
            f"/adage/v1/years/{booking.educationalBooking.educationalYear.adageId}/educational_institution/{booking.educationalBooking.educationalInstitution.institutionId}/prebookings?status=PENDING&redactorEmail={redactor.email}"
        )

        assert response.status_code == 200
        stock = booking.stock
        offer = stock.offer
        venue = offer.venue
        educational_booking = booking.educationalBooking
        assert response.json == {
            "prebookings": [
                {
                    "accessibility": "Non accessible",
                    "address": f"{venue.address}, {venue.postalCode} {venue.city}",
                    "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
                    "cancellationDate": None,
                    "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
                    "city": venue.city,
                    "confirmationDate": None,
                    "confirmationLimitDate": format_into_utc_date(educational_booking.confirmationLimitDate),
                    "contact": {
                        "email": None,
                        "phone": None,
                    },
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
                    "price": float(booking.amount),
                    "quantity": booking.quantity,
                    "redactor": {
                        "email": "jean.doux@example.com",
                        "redactorFirstName": "Jean",
                        "redactorLastName": "Doudou",
                        "redactorCivility": "M.",
                    },
                    "UAICode": educational_booking.educationalInstitution.institutionId,
                    "yearId": int(educational_booking.educationalYearId),
                    "status": "PENDING",
                    "subcategoryLabel": "Séance de cinéma",
                    "venueTimezone": venue.timezone,
                    "totalAmount": float(booking.total_amount),
                    "url": offer_app_link(offer),
                    "withdrawalDetails": offer.withdrawalDetails,
                    "domainIds": [],
                    "domainLabels": [],
                }
            ],
        }
