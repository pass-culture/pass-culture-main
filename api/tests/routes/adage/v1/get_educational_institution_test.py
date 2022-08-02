from typing import Any

import pytest

from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import EducationalDepositFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.offers.utils import offer_app_link
from pcapi.core.testing import assert_num_queries
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_educational_institution(self, client: Any) -> None:
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
        booking = CollectiveBookingFactory(
            educationalRedactor=redactor,
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
        )
        other_educational_year = EducationalYearFactory(adageId="toto")
        other_educational_institution = EducationalInstitutionFactory(institutionId="tata")
        CollectiveBookingFactory(educationalYear=other_educational_year)
        CollectiveBookingFactory(educationalInstitution=other_educational_institution)
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

        response = client.with_eac_token().get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}"
        )

        assert response.status_code == 200

        stock = booking.collectiveStock
        offer = stock.collectiveOffer
        venue = offer.venue
        assert response.json == {
            "credit": 2000,
            "isFinal": True,
            "prebookings": [
                {
                    "address": offer.offerVenue["otherAddress"],
                    "accessibility": "Non accessible",
                    "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
                    "cancellationDate": None,
                    "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
                    "city": venue.city,
                    "confirmationDate": format_into_utc_date(booking.confirmationDate)
                    if booking.confirmationDate
                    else None,
                    "confirmationLimitDate": format_into_utc_date(booking.confirmationLimitDate),
                    "contact": {"email": offer.contactEmail, "phone": offer.contactPhone},
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
                    "participants": [students.value for students in offer.students],
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

    def test_get_educational_institution_num_queries(self, client: Any) -> None:
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
        CollectiveBookingFactory.create_batch(
            10,
            educationalRedactor=redactor,
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
        )
        other_educational_year = EducationalYearFactory(adageId="toto")
        other_educational_institution = EducationalInstitutionFactory(institutionId="tata")
        CollectiveBookingFactory(educationalYear=other_educational_year)
        CollectiveBookingFactory(educationalInstitution=other_educational_institution)
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

        adage_id = educational_year.adageId
        institution_id = educational_institution.institutionId

        n_queries = 0
        n_queries += 1  # Check for educational institution
        n_queries += 1  # Get needed data
        n_queries += 1  # Get deposit

        with assert_num_queries(n_queries):
            client.with_eac_token().get(f"/adage/v1/years/{adage_id}/educational_institution/{institution_id}")

    def test_get_educational_institution_without_deposit(self, client: Any) -> None:
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()

        response = client.with_eac_token().get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}"
        )

        assert response.status_code == 200

        assert response.json == {
            "credit": 0,
            "isFinal": False,
            "prebookings": [],
        }


class Returns404Test:
    def test_get_educational_institution_not_found(self, client: Any, db_session: Any) -> None:
        educational_year = EducationalYearFactory()
        EducationalInstitutionFactory()

        response = client.with_eac_token().get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/UNKNOWN"
        )

        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_INSTITUTION_NOT_FOUND"}
