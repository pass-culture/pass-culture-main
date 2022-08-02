import pytest

from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.offers.utils import offer_app_link
from pcapi.core.testing import assert_num_queries
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_get_collective_bookings(self, client) -> None:  # type: ignore [no-untyped-def]
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking1 = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="CONFIRMED",
        )
        booking2 = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="PENDING",
        )

        client = client.with_eac_token()

        with assert_num_queries(3):
            response = client.get(
                f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}/prebookings"
            )

        assert response.status_code == 200
        stock1 = booking1.collectiveStock
        offer1 = stock1.collectiveOffer
        venue1 = offer1.venue

        stock2 = booking2.collectiveStock
        offer2 = stock2.collectiveOffer
        venue2 = offer2.venue

        assert response.json == {
            "prebookings": [
                {
                    "address": offer1.offerVenue["otherAddress"],
                    "accessibility": "Non accessible",
                    "beginningDatetime": format_into_utc_date(stock1.beginningDatetime),
                    "cancellationDate": None,
                    "cancellationLimitDate": format_into_utc_date(booking1.cancellationLimitDate),
                    "city": venue1.city,
                    "confirmationDate": format_into_utc_date(booking1.confirmationDate),
                    "confirmationLimitDate": format_into_utc_date(booking1.confirmationLimitDate),
                    "contact": {"email": offer1.contactEmail, "phone": offer1.contactPhone},
                    "coordinates": {
                        "latitude": float(venue1.latitude),
                        "longitude": float(venue1.longitude),
                    },
                    "creationDate": format_into_utc_date(booking1.dateCreated),
                    "description": offer1.description,
                    "durationMinutes": offer1.durationMinutes,
                    "expirationDate": None,
                    "id": booking1.id,
                    "isDigital": False,
                    "venueName": venue1.name,
                    "name": offer1.name,
                    "numberOfTickets": stock1.numberOfTickets,
                    "participants": [students.value for students in offer1.students],
                    "priceDetail": stock1.priceDetail,
                    "postalCode": venue1.postalCode,
                    "price": float(stock1.price),
                    "quantity": 1,
                    "redactor": {
                        "email": booking1.educationalRedactor.email,
                        "redactorFirstName": booking1.educationalRedactor.firstName,
                        "redactorLastName": booking1.educationalRedactor.lastName,
                        "redactorCivility": booking1.educationalRedactor.civility,
                    },
                    "UAICode": booking1.educationalInstitution.institutionId,
                    "yearId": int(booking1.educationalYearId),
                    "status": "CONFIRMED",
                    "subcategoryLabel": offer1.subcategory.app_label,
                    "venueTimezone": venue1.timezone,
                    "totalAmount": float(stock1.price),
                    "url": offer_app_link(offer1),
                    "withdrawalDetails": None,
                    "domainIds": [domain.id for domain in offer1.domains],
                    "domainLabels": [domain.name for domain in offer1.domains],
                    "interventionArea": offer1.interventionArea,
                },
                {
                    "address": offer2.offerVenue["otherAddress"],
                    "accessibility": "Non accessible",
                    "beginningDatetime": format_into_utc_date(stock2.beginningDatetime),
                    "cancellationDate": None,
                    "cancellationLimitDate": format_into_utc_date(booking2.cancellationLimitDate),
                    "city": venue2.city,
                    "confirmationDate": format_into_utc_date(booking2.confirmationDate),
                    "confirmationLimitDate": format_into_utc_date(booking2.confirmationLimitDate),
                    "contact": {"email": offer2.contactEmail, "phone": offer2.contactPhone},
                    "coordinates": {
                        "latitude": float(venue2.latitude),
                        "longitude": float(venue2.longitude),
                    },
                    "creationDate": format_into_utc_date(booking2.dateCreated),
                    "description": offer2.description,
                    "durationMinutes": offer2.durationMinutes,
                    "expirationDate": None,
                    "id": booking2.id,
                    "isDigital": False,
                    "venueName": venue2.name,
                    "name": offer2.name,
                    "numberOfTickets": stock2.numberOfTickets,
                    "participants": [students.value for students in offer2.students],
                    "priceDetail": stock2.priceDetail,
                    "postalCode": venue2.postalCode,
                    "price": float(stock2.price),
                    "quantity": 1,
                    "redactor": {
                        "email": booking2.educationalRedactor.email,
                        "redactorFirstName": booking2.educationalRedactor.firstName,
                        "redactorLastName": booking2.educationalRedactor.lastName,
                        "redactorCivility": booking2.educationalRedactor.civility,
                    },
                    "UAICode": booking2.educationalInstitution.institutionId,
                    "yearId": int(booking2.educationalYearId),
                    "status": "PENDING",
                    "subcategoryLabel": offer2.subcategory.app_label,
                    "venueTimezone": venue2.timezone,
                    "totalAmount": float(stock2.price),
                    "url": offer_app_link(offer2),
                    "withdrawalDetails": None,
                    "domainIds": [domain.id for domain in offer2.domains],
                    "domainLabels": [domain.name for domain in offer2.domains],
                    "interventionArea": offer2.interventionArea,
                },
            ]
        }

    def test_get_collective_bookings_filter_UAI(self, client) -> None:  # type: ignore [no-untyped-def]
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking1 = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="CONFIRMED",
        )
        other_educational_institution = EducationalInstitutionFactory(institutionId="Pouet")
        CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=other_educational_institution,
            status="PENDING",
        )

        client = client.with_eac_token()

        response = client.get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}/prebookings"
        )

        assert response.status_code == 200
        stock1 = booking1.collectiveStock
        offer1 = stock1.collectiveOffer
        venue1 = offer1.venue

        assert response.json == {
            "prebookings": [
                {
                    "address": offer1.offerVenue["otherAddress"],
                    "accessibility": "Non accessible",
                    "beginningDatetime": format_into_utc_date(stock1.beginningDatetime),
                    "cancellationDate": None,
                    "cancellationLimitDate": format_into_utc_date(booking1.cancellationLimitDate),
                    "city": venue1.city,
                    "confirmationDate": format_into_utc_date(booking1.confirmationDate),
                    "confirmationLimitDate": format_into_utc_date(booking1.confirmationLimitDate),
                    "contact": {"email": offer1.contactEmail, "phone": offer1.contactPhone},
                    "coordinates": {
                        "latitude": float(venue1.latitude),
                        "longitude": float(venue1.longitude),
                    },
                    "creationDate": format_into_utc_date(booking1.dateCreated),
                    "description": offer1.description,
                    "durationMinutes": offer1.durationMinutes,
                    "expirationDate": None,
                    "id": booking1.id,
                    "isDigital": False,
                    "venueName": venue1.name,
                    "name": offer1.name,
                    "numberOfTickets": stock1.numberOfTickets,
                    "participants": [students.value for students in offer1.students],
                    "priceDetail": stock1.priceDetail,
                    "postalCode": venue1.postalCode,
                    "price": float(stock1.price),
                    "quantity": 1,
                    "redactor": {
                        "email": booking1.educationalRedactor.email,
                        "redactorFirstName": booking1.educationalRedactor.firstName,
                        "redactorLastName": booking1.educationalRedactor.lastName,
                        "redactorCivility": booking1.educationalRedactor.civility,
                    },
                    "UAICode": booking1.educationalInstitution.institutionId,
                    "yearId": int(booking1.educationalYearId),
                    "status": "CONFIRMED",
                    "subcategoryLabel": offer1.subcategory.app_label,
                    "venueTimezone": venue1.timezone,
                    "totalAmount": float(stock1.price),
                    "url": offer_app_link(offer1),
                    "withdrawalDetails": None,
                    "domainIds": [domain.id for domain in offer1.domains],
                    "domainLabels": [domain.name for domain in offer1.domains],
                    "interventionArea": offer1.interventionArea,
                }
            ]
        }

    def test_get_collective_bookings_filter_year_id(self, client) -> None:  # type: ignore [no-untyped-def]
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking1 = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="CONFIRMED",
        )
        other_educational_year = EducationalYearFactory(adageId="Pouet")
        CollectiveBookingFactory(
            educationalYear=other_educational_year,
            educationalInstitution=educational_institution,
            status="PENDING",
        )

        client = client.with_eac_token()

        response = client.get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}/prebookings"
        )

        assert response.status_code == 200
        stock1 = booking1.collectiveStock
        offer1 = stock1.collectiveOffer
        venue1 = offer1.venue

        assert response.json == {
            "prebookings": [
                {
                    "address": offer1.offerVenue["otherAddress"],
                    "accessibility": "Non accessible",
                    "beginningDatetime": format_into_utc_date(stock1.beginningDatetime),
                    "cancellationDate": None,
                    "cancellationLimitDate": format_into_utc_date(booking1.cancellationLimitDate),
                    "city": venue1.city,
                    "confirmationDate": format_into_utc_date(booking1.confirmationDate),
                    "confirmationLimitDate": format_into_utc_date(booking1.confirmationLimitDate),
                    "contact": {"email": offer1.contactEmail, "phone": offer1.contactPhone},
                    "coordinates": {
                        "latitude": float(venue1.latitude),
                        "longitude": float(venue1.longitude),
                    },
                    "creationDate": format_into_utc_date(booking1.dateCreated),
                    "description": offer1.description,
                    "durationMinutes": offer1.durationMinutes,
                    "expirationDate": None,
                    "id": booking1.id,
                    "isDigital": False,
                    "venueName": venue1.name,
                    "name": offer1.name,
                    "numberOfTickets": stock1.numberOfTickets,
                    "participants": [students.value for students in offer1.students],
                    "priceDetail": stock1.priceDetail,
                    "postalCode": venue1.postalCode,
                    "price": float(stock1.price),
                    "quantity": 1,
                    "redactor": {
                        "email": booking1.educationalRedactor.email,
                        "redactorFirstName": booking1.educationalRedactor.firstName,
                        "redactorLastName": booking1.educationalRedactor.lastName,
                        "redactorCivility": booking1.educationalRedactor.civility,
                    },
                    "UAICode": booking1.educationalInstitution.institutionId,
                    "yearId": int(booking1.educationalYearId),
                    "status": "CONFIRMED",
                    "subcategoryLabel": offer1.subcategory.app_label,
                    "venueTimezone": venue1.timezone,
                    "totalAmount": float(stock1.price),
                    "url": offer_app_link(offer1),
                    "withdrawalDetails": None,
                    "domainIds": [domain.id for domain in offer1.domains],
                    "domainLabels": [domain.name for domain in offer1.domains],
                    "interventionArea": offer1.interventionArea,
                }
            ]
        }

    def test_get_collective_bookings_filter_redactor_email(self, client) -> None:  # type: ignore [no-untyped-def]
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking1 = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="CONFIRMED",
        )
        CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="PENDING",
            educationalRedactor__email="redactor@example.com",
        )

        client = client.with_eac_token()

        response = client.get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}/prebookings?redactorEmail={booking1.educationalRedactor.email}"
        )

        assert response.status_code == 200
        stock1 = booking1.collectiveStock
        offer1 = stock1.collectiveOffer
        venue1 = offer1.venue

        assert response.json == {
            "prebookings": [
                {
                    "address": offer1.offerVenue["otherAddress"],
                    "accessibility": "Non accessible",
                    "beginningDatetime": format_into_utc_date(stock1.beginningDatetime),
                    "cancellationDate": None,
                    "cancellationLimitDate": format_into_utc_date(booking1.cancellationLimitDate),
                    "city": venue1.city,
                    "confirmationDate": format_into_utc_date(booking1.confirmationDate),
                    "confirmationLimitDate": format_into_utc_date(booking1.confirmationLimitDate),
                    "contact": {"email": offer1.contactEmail, "phone": offer1.contactPhone},
                    "coordinates": {
                        "latitude": float(venue1.latitude),
                        "longitude": float(venue1.longitude),
                    },
                    "creationDate": format_into_utc_date(booking1.dateCreated),
                    "description": offer1.description,
                    "durationMinutes": offer1.durationMinutes,
                    "expirationDate": None,
                    "id": booking1.id,
                    "isDigital": False,
                    "venueName": venue1.name,
                    "name": offer1.name,
                    "numberOfTickets": stock1.numberOfTickets,
                    "participants": [students.value for students in offer1.students],
                    "priceDetail": stock1.priceDetail,
                    "postalCode": venue1.postalCode,
                    "price": float(stock1.price),
                    "quantity": 1,
                    "redactor": {
                        "email": booking1.educationalRedactor.email,
                        "redactorFirstName": booking1.educationalRedactor.firstName,
                        "redactorLastName": booking1.educationalRedactor.lastName,
                        "redactorCivility": booking1.educationalRedactor.civility,
                    },
                    "UAICode": booking1.educationalInstitution.institutionId,
                    "yearId": int(booking1.educationalYearId),
                    "status": "CONFIRMED",
                    "subcategoryLabel": offer1.subcategory.app_label,
                    "venueTimezone": venue1.timezone,
                    "totalAmount": float(stock1.price),
                    "url": offer_app_link(offer1),
                    "withdrawalDetails": None,
                    "domainIds": [domain.id for domain in offer1.domains],
                    "domainLabels": [domain.name for domain in offer1.domains],
                    "interventionArea": offer1.interventionArea,
                }
            ]
        }

    def test_get_collective_bookings_filter_status(self, client) -> None:  # type: ignore [no-untyped-def]
        educational_year = EducationalYearFactory()
        educational_institution = EducationalInstitutionFactory()
        booking1 = CollectiveBookingFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            status="CONFIRMED",
        )
        other_educational_year = EducationalYearFactory(adageId="Pouet")
        CollectiveBookingFactory(
            educationalYear=other_educational_year,
            educationalInstitution=educational_institution,
            status="PENDING",
        )

        client = client.with_eac_token()

        response = client.get(
            f"/adage/v1/years/{educational_year.adageId}/educational_institution/{educational_institution.institutionId}/prebookings?status=CONFIRMED"
        )

        assert response.status_code == 200
        stock1 = booking1.collectiveStock
        offer1 = stock1.collectiveOffer
        venue1 = offer1.venue

        assert response.json == {
            "prebookings": [
                {
                    "address": offer1.offerVenue["otherAddress"],
                    "accessibility": "Non accessible",
                    "beginningDatetime": format_into_utc_date(stock1.beginningDatetime),
                    "cancellationDate": None,
                    "cancellationLimitDate": format_into_utc_date(booking1.cancellationLimitDate),
                    "city": venue1.city,
                    "confirmationDate": format_into_utc_date(booking1.confirmationDate),
                    "confirmationLimitDate": format_into_utc_date(booking1.confirmationLimitDate),
                    "contact": {"email": offer1.contactEmail, "phone": offer1.contactPhone},
                    "coordinates": {
                        "latitude": float(venue1.latitude),
                        "longitude": float(venue1.longitude),
                    },
                    "creationDate": format_into_utc_date(booking1.dateCreated),
                    "description": offer1.description,
                    "durationMinutes": offer1.durationMinutes,
                    "expirationDate": None,
                    "id": booking1.id,
                    "isDigital": False,
                    "venueName": venue1.name,
                    "name": offer1.name,
                    "numberOfTickets": stock1.numberOfTickets,
                    "participants": [students.value for students in offer1.students],
                    "priceDetail": stock1.priceDetail,
                    "postalCode": venue1.postalCode,
                    "price": float(stock1.price),
                    "quantity": 1,
                    "redactor": {
                        "email": booking1.educationalRedactor.email,
                        "redactorFirstName": booking1.educationalRedactor.firstName,
                        "redactorLastName": booking1.educationalRedactor.lastName,
                        "redactorCivility": booking1.educationalRedactor.civility,
                    },
                    "UAICode": booking1.educationalInstitution.institutionId,
                    "yearId": int(booking1.educationalYearId),
                    "status": "CONFIRMED",
                    "subcategoryLabel": offer1.subcategory.app_label,
                    "venueTimezone": venue1.timezone,
                    "totalAmount": float(stock1.price),
                    "url": offer_app_link(offer1),
                    "withdrawalDetails": None,
                    "domainIds": [domain.id for domain in offer1.domains],
                    "domainLabels": [domain.name for domain in offer1.domains],
                    "interventionArea": offer1.interventionArea,
                }
            ]
        }
