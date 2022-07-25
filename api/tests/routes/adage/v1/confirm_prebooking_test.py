from datetime import datetime
from decimal import Decimal

from freezegun import freeze_time
import pytest

from pcapi.core.bookings.models import Booking
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import EducationalDepositFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import Ministry
from pcapi.core.offers.utils import offer_app_link
from pcapi.routes.adage.v1.serialization import constants
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2021-10-15 09:00:00")
class Returns200Test:
    def test_confirm_collective_prebooking(self, client) -> None:  # type: ignore [no-untyped-def]
        redactor = EducationalRedactorFactory(
            civility="Mme",
            firstName="Jeanne",
            lastName="Dodu",
            email="jeanne.dodu@example.com",
        )
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=True,
        )
        CollectiveBookingFactory(
            collectiveStock__price=Decimal(20.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.CONFIRMED,
        )

        booking = CollectiveBookingFactory(
            collectiveStock__price=Decimal(20.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalRedactor=redactor,
            status=CollectiveBookingStatus.PENDING,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 200
        stock = booking.collectiveStock
        offer = stock.collectiveOffer
        venue = offer.venue
        assert response.json == {
            "address": offer.offerVenue["otherAddress"],
            "accessibility": "Non accessible",
            "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
            "cancellationDate": None,
            "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
            "city": venue.city,
            "confirmationDate": "2021-10-15T09:00:00Z",
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
            "participants": [student.value for student in offer.students],
            "priceDetail": stock.priceDetail,
            "postalCode": venue.postalCode,
            "price": float(stock.price),
            "quantity": 1,
            "redactor": {
                "email": "jeanne.dodu@example.com",
                "redactorFirstName": "Jeanne",
                "redactorLastName": "Dodu",
                "redactorCivility": "Mme",
            },
            "UAICode": booking.educationalInstitution.institutionId,
            "yearId": int(booking.educationalYearId),
            "status": "CONFIRMED",
            "subcategoryLabel": offer.subcategory.app_label,
            "venueTimezone": venue.timezone,
            "totalAmount": float(stock.price),
            "url": offer_app_link(offer),
            "withdrawalDetails": None,
            "domainLabels": [domain.name for domain in offer.domains],
            "domainIds": [domain.id for domain in offer.domains],
        }
        assert (
            CollectiveBooking.query.filter(CollectiveBooking.id == booking.id).one().status
            == CollectiveBookingStatus.CONFIRMED
        )

    def test_insufficient_ministry_fund_other_ministry(self, client) -> None:  # type: ignore [no-untyped-def]
        educational_institution = EducationalInstitutionFactory()
        educational_institution2 = EducationalInstitutionFactory()
        educational_institution3 = EducationalInstitutionFactory()

        educational_year = EducationalYearFactory(adageId="1")
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(2000.00),
            isFinal=True,
        )
        EducationalDepositFactory(
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            amount=Decimal(10000.00),
            isFinal=True,
        )
        EducationalDepositFactory(
            educationalInstitution=educational_institution3,
            educationalYear=educational_year,
            amount=Decimal(10000.00),
            isFinal=True,
            ministry=Ministry.AGRICULTURE,
        )
        CollectiveBookingFactory(
            collectiveStock__price=Decimal(4800.00),
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.CONFIRMED,
            confirmationLimitDate=datetime(2021, 10, 21, 10),
        )
        booking = CollectiveBookingFactory(
            collectiveStock__price=Decimal(300.00),
            educationalInstitution=educational_institution3,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.PENDING,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")
        assert response.status_code == 200

    def test_sufficient_ministry_fund(self, client) -> None:  # type: ignore [no-untyped-def]
        educational_institution = EducationalInstitutionFactory()
        educational_institution2 = EducationalInstitutionFactory()
        educational_institution3 = EducationalInstitutionFactory()

        educational_year = EducationalYearFactory(adageId="1")
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(2000.00),
            isFinal=True,
        )
        EducationalDepositFactory(
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            amount=Decimal(10000.00),
            isFinal=True,
        )
        EducationalDepositFactory(
            educationalInstitution=educational_institution3,
            educationalYear=educational_year,
            amount=Decimal(10000.00),
            isFinal=True,
            ministry=Ministry.AGRICULTURE,
        )
        CollectiveBookingFactory(
            collectiveStock__price=Decimal(200.00),
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.CONFIRMED,
            confirmationLimitDate=datetime(2021, 10, 21, 10),
        )

        CollectiveBookingFactory(
            collectiveStock__price=Decimal(200.00),
            educationalInstitution=educational_institution3,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.CONFIRMED,
            confirmationLimitDate=datetime(2021, 10, 21, 10),
        )

        booking = CollectiveBookingFactory(
            collectiveStock__price=Decimal(300.00),
            educationalInstitution=educational_institution3,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.PENDING,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")
        assert response.status_code == 200

    def test_out_of_minitry_check_dates(self, client) -> None:  # type: ignore [no-untyped-def]
        educational_institution = EducationalInstitutionFactory()
        educational_institution2 = EducationalInstitutionFactory()

        educational_year = EducationalYearFactory(adageId="1")
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(2000.00),
            isFinal=True,
        )
        EducationalDepositFactory(
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            amount=Decimal(10000.00),
            isFinal=True,
        )
        CollectiveBookingFactory(
            collectiveStock__price=Decimal(4000.00),
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.CONFIRMED,
            confirmationLimitDate=datetime(2021, 10, 21, 10),
        )

        booking = CollectiveBookingFactory(
            collectiveStock__price=Decimal(300.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.PENDING,
            confirmationLimitDate=datetime(2022, 2, 15, 10),
            collectiveStock__beginningDatetime=datetime(2022, 3, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")
        assert response.status_code == 200


@freeze_time("2021-10-15 09:00:00")
class ReturnsErrorTest:
    def test_no_educational_booking(self, client) -> None:  # type: ignore [no-untyped-def]
        client = client.with_eac_token()
        response = client.post("/adage/v1/prebookings/404/confirm")

        assert response.status_code == 404
        assert response.json == {"code": constants.EDUCATIONAL_BOOKING_NOT_FOUND}

    def test_no_collective_booking(self, client) -> None:  # type: ignore [no-untyped-def]
        client = client.with_eac_token()
        response = client.post("/adage/v1/prebookings/404/confirm")

        assert response.status_code == 404
        assert response.json == {"code": constants.EDUCATIONAL_BOOKING_NOT_FOUND}

    def test_no_deposit_for_collective_bookings(self, client) -> None:  # type: ignore [no-untyped-def]
        booking = CollectiveBookingFactory(
            collectiveStock__price=Decimal(20.00),
            status=CollectiveBookingStatus.PENDING,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 404
        assert response.json == {"code": "DEPOSIT_NOT_FOUND"}

    def test_insufficient_fund_for_collective_bookings(self, client) -> None:  # type: ignore [no-untyped-def]
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(100.00),
            isFinal=True,
        )
        booking = CollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.PENDING,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_FUND"}

    def test_insufficient_ministry_fund_for_collective_bookings(self, client) -> None:  # type: ignore [no-untyped-def]
        educational_institution = EducationalInstitutionFactory()
        educational_institution2 = EducationalInstitutionFactory()

        educational_year = EducationalYearFactory(adageId="1")
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(2000.00),
            isFinal=True,
        )
        EducationalDepositFactory(
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            amount=Decimal(13000.00),
            isFinal=True,
        )
        CollectiveBookingFactory(
            collectiveStock__price=Decimal(4800.00),
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.CONFIRMED,
            confirmationLimitDate=datetime(2021, 10, 21, 10),
        )
        booking = CollectiveBookingFactory(
            collectiveStock__price=Decimal(300.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.PENDING,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")
        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_MINISTRY_FUND"}

    def test_insufficient_temporary_fund_for_collective_bookings(self, client) -> None:  # type: ignore [no-untyped-def]
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400.00),
            isFinal=False,
        )
        booking = CollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.PENDING,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_FUND_DEPOSIT_NOT_FINAL"}

    def test_collective_booking_is_cancelled(self, client) -> None:  # type: ignore [no-untyped-def]
        booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.CANCELLED,
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "EDUCATIONAL_BOOKING_IS_CANCELLED"}

    @freeze_time("2021-08-05 15:00:00")
    def test_confirmation_limit_date_has_passed_for_collective_bookings(  # type: ignore [no-untyped-def]
        self, client
    ) -> None:
        booking: Booking = CollectiveBookingFactory(
            confirmationLimitDate=datetime(2021, 8, 5, 14),
            status=CollectiveBookingStatus.PENDING,
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "CONFIRMATION_LIMIT_DATE_HAS_PASSED"}
