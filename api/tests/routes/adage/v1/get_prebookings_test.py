from typing import Any

import pytest

from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.models import StudentLevels
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
        booking = CollectiveBookingFactory(
            educationalYear=educationalYear,
            educationalInstitution=educationalInstitution,
            educationalRedactor=redactor,
            collectiveStock__collectiveOffer__description=None,
            collectiveStock__collectiveOffer__students=[
                StudentLevels.CAP1,
                StudentLevels.CAP2,
                StudentLevels.GENERAL2,
                StudentLevels.GENERAL1,
            ],
            collectiveStock__collectiveOffer__offerVenue={
                "addressType": "other",
                "otherAddress": "1 rue des polissons, Paris 75017",
                "venueId": "",
            },
            collectiveStock__collectiveOffer__contactEmail="miss.rond@point.com",
            collectiveStock__collectiveOffer__contactPhone="01010100101",
            collectiveStock__collectiveOffer__audioDisabilityCompliant=True,
            collectiveStock__collectiveOffer__visualDisabilityCompliant=True,
            collectiveStock__collectiveOffer__subcategoryId="SEANCE_CINE",
        )
        other_educational_year = EducationalYearFactory(adageId="adageId")
        other_educational_institution = EducationalInstitutionFactory(institutionId="institutionId")
        CollectiveBookingFactory(educationalYear=other_educational_year)
        CollectiveBookingFactory(educationalInstitution=other_educational_institution)

        response = client.with_eac_token().get(
            f"/adage/v1/years/{booking.educationalYear.adageId}/educational_institution/{booking.educationalInstitution.institutionId}/prebookings"
        )

        assert response.status_code == 200

        stock = booking.collectiveStock
        offer = stock.collectiveOffer
        venue = offer.venue
        assert response.json == {
            "prebookings": [
                {
                    "accessibility": "Auditif, Visuel",
                    "address": "1 rue des polissons, Paris 75017",
                    "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
                    "cancellationDate": None,
                    "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
                    "city": venue.city,
                    "confirmationDate": format_into_utc_date(booking.confirmationDate),
                    "confirmationLimitDate": format_into_utc_date(booking.confirmationLimitDate),
                    "contact": {"email": "miss.rond@point.com", "phone": "01010100101"},
                    "coordinates": {
                        "latitude": float(venue.latitude),
                        "longitude": float(venue.longitude),
                    },
                    "creationDate": format_into_utc_date(booking.dateCreated),
                    "description": offer.description,
                    "durationMinutes": offer.durationMinutes,
                    "expirationDate": None,
                    "id": booking.id,
                    "isDigital": False,
                    "venueName": venue.name,
                    "name": offer.name,
                    "numberOfTickets": stock.numberOfTickets,
                    "participants": [
                        "CAP - 1re ann\u00e9e",
                        "CAP - 2e ann\u00e9e",
                        "Lyc\u00e9e - Seconde",
                        "Lyc\u00e9e - Premi\u00e8re",
                    ],
                    "priceDetail": stock.priceDetail,
                    "postalCode": venue.postalCode,
                    "price": float(stock.price),
                    "quantity": 1,
                    "redactor": {
                        "email": "jean.doux@example.com",
                        "redactorFirstName": "Jean",
                        "redactorLastName": "Doudou",
                        "redactorCivility": "M.",
                    },
                    "UAICode": booking.educationalInstitution.institutionId,
                    "yearId": int(booking.educationalYearId),
                    "status": "CONFIRMED",
                    "subcategoryLabel": offer.subcategory.app_label,
                    "venueTimezone": venue.timezone,
                    "totalAmount": float(stock.price),
                    "url": offer_app_link(offer),
                    "withdrawalDetails": None,
                    "domainIds": [domain.id for domain in offer.domains],
                    "domainLabels": [domain.name for domain in offer.domains],
                    "interventionArea": offer.interventionArea,
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
        CollectiveBookingFactory(
            educationalRedactor=redactor,
            educationalYear=educationalYear,
            educationalInstitution=educationalInstitution,
            status="CONFIRMED",
        )
        CollectiveBookingFactory(
            educationalRedactor=another_redactor,
            educationalYear=educationalYear,
            educationalInstitution=educationalInstitution,
            status="PENDING",
        )
        booking = CollectiveBookingFactory(
            educationalRedactor=redactor,
            educationalYear=educationalYear,
            educationalInstitution=educationalInstitution,
            status="PENDING",
            collectiveStock__collectiveOffer__subcategoryId="SEANCE_CINE",
        )

        response = client.with_eac_token().get(
            f"/adage/v1/years/{booking.educationalYear.adageId}/educational_institution/{booking.educationalInstitution.institutionId}/prebookings?status=PENDING&redactorEmail={redactor.email}"
        )

        assert response.status_code == 200
        stock = booking.collectiveStock
        offer = stock.collectiveOffer
        venue = offer.venue
        assert response.json == {
            "prebookings": [
                {
                    "accessibility": "Non accessible",
                    "address": "1 rue des polissons, Paris 75017",
                    "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
                    "cancellationDate": None,
                    "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
                    "city": venue.city,
                    "confirmationDate": format_into_utc_date(booking.confirmationDate),
                    "confirmationLimitDate": format_into_utc_date(booking.confirmationLimitDate),
                    "contact": {
                        "email": offer.contactEmail,
                        "phone": offer.contactPhone,
                    },
                    "coordinates": {
                        "latitude": float(venue.latitude),
                        "longitude": float(venue.longitude),
                    },
                    "creationDate": format_into_utc_date(booking.dateCreated),
                    "description": offer.description,
                    "durationMinutes": offer.durationMinutes,
                    "expirationDate": None,
                    "id": booking.id,
                    "isDigital": False,
                    "venueName": venue.name,
                    "name": offer.name,
                    "numberOfTickets": stock.numberOfTickets,
                    "participants": [student.value for student in offer.students],
                    "priceDetail": stock.priceDetail,
                    "postalCode": venue.postalCode,
                    "price": float(stock.price),
                    "quantity": 1,
                    "redactor": {
                        "email": "jean.doux@example.com",
                        "redactorFirstName": "Jean",
                        "redactorLastName": "Doudou",
                        "redactorCivility": "M.",
                    },
                    "UAICode": booking.educationalInstitution.institutionId,
                    "yearId": int(booking.educationalYearId),
                    "status": "PENDING",
                    "subcategoryLabel": "Séance de cinéma",
                    "venueTimezone": venue.timezone,
                    "totalAmount": float(stock.price),
                    "url": offer_app_link(offer),
                    "withdrawalDetails": None,
                    "domainIds": [domain.id for domain in offer.domains],
                    "domainLabels": [domain.name for domain in offer.domains],
                    "interventionArea": offer.interventionArea,
                }
            ],
        }
