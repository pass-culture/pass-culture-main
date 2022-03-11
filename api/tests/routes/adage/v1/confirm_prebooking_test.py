from datetime import datetime
from decimal import Decimal

from freezegun import freeze_time
import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.educational.models import EducationalDeposit
from pcapi.core.offers.utils import offer_app_link
from pcapi.routes.adage.v1.serialization import constants
from pcapi.utils.date import format_into_utc_date


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2021-10-15 09:00:00")
class Returns200Test:
    def test_confirm_prebooking(self, client) -> None:
        redactor = EducationalRedactorFactory(
            civility="Mme",
            firstName="Jeanne",
            lastName="Dodu",
            email="jeanne.dodu@example.com",
        )
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=True,
        )
        EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.CONFIRMED,
        )

        booking = EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            educationalBooking__educationalRedactor=redactor,
            status=BookingStatus.PENDING,
            educationalBooking__confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/confirm")

        assert response.status_code == 200
        stock = booking.stock
        offer = stock.offer
        venue = offer.venue
        educational_booking = booking.educationalBooking

        assert response.json == {
            "address": f"{venue.address}, {venue.postalCode} {venue.city}",
            "accessibility": "Non accessible",
            "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
            "cancellationDate": None,
            "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
            "city": venue.city,
            "confirmationDate": "2021-10-15T09:00:00Z",
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
                "email": "jeanne.dodu@example.com",
                "redactorFirstName": "Jeanne",
                "redactorLastName": "Dodu",
                "redactorCivility": "Mme",
            },
            "UAICode": educational_booking.educationalInstitution.institutionId,
            "yearId": int(educational_booking.educationalYearId),
            "status": "CONFIRMED",
            "subcategoryLabel": "Séance de cinéma",
            "venueTimezone": venue.timezone,
            "totalAmount": booking.total_amount,
            "url": offer_app_link(offer),
            "withdrawalDetails": offer.withdrawalDetails,
        }
        assert Booking.query.filter(Booking.id == booking.id).one().status == BookingStatus.CONFIRMED

    def test_confirm_collective_booking(self, client) -> None:
        redactor = EducationalRedactorFactory(
            civility="Mme",
            firstName="Jeanne",
            lastName="Dodu",
            email="jeanne.dodu@example.com",
        )
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=True,
        )
        EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.CONFIRMED,
        )

        booking = EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            educationalBooking__educationalRedactor=redactor,
            status=BookingStatus.PENDING,
            educationalBooking__confirmationLimitDate=datetime(2021, 10, 15, 15),
        )
        CollectiveBookingFactory(
            collectiveStock__price=Decimal(20.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            status=CollectiveBookingStatus.PENDING,
            bookingId=booking.id,
            confirmationLimitDate=datetime(2021, 10, 15, 15),
        )

        client = client.with_eac_token()
        client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/confirm")

        assert (
            CollectiveBooking.query.filter(CollectiveBooking.bookingId == booking.id).one().status
            == CollectiveBookingStatus.CONFIRMED
        )


@freeze_time("2021-10-15 09:00:00")
class ReturnsErrorTest:
    def test_no_educational_booking(self, client) -> None:
        client = client.with_eac_token()
        response = client.post("/adage/v1/prebookings/404/confirm")

        assert response.status_code == 404
        assert response.json == {"code": constants.EDUCATIONAL_BOOKING_NOT_FOUND}

    def test_no_deposit(self, client) -> None:
        booking = EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            status=BookingStatus.PENDING,
            educationalBooking__confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/confirm")

        assert response.status_code == 404
        assert response.json == {"code": "DEPOSIT_NOT_FOUND"}

    def test_insufficient_fund(self, client) -> None:
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(100.00),
            isFinal=True,
        )
        booking = EducationalBookingFactory(
            amount=Decimal(400.00),
            quantity=1,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.PENDING,
            educationalBooking__confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_FUND"}

    def test_insufficient_temporary_fund(self, client) -> None:
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        EducationalDeposit(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(400.00),
            isFinal=False,
        )
        booking = EducationalBookingFactory(
            amount=Decimal(400.00),
            quantity=1,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.PENDING,
            educationalBooking__confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_FUND_DEPOSIT_NOT_FINAL"}

    def test_educational_booking_is_refused(self, client) -> None:
        booking = EducationalBookingFactory(
            educationalBooking__status=EducationalBookingStatus.REFUSED,
            status=BookingStatus.CANCELLED,
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "EDUCATIONAL_BOOKING_IS_REFUSED"}

    def test_educational_booking_is_cancelled(self, client) -> None:
        booking = EducationalBookingFactory(
            status=BookingStatus.CANCELLED,
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "EDUCATIONAL_BOOKING_IS_CANCELLED"}

    @freeze_time("2021-08-05 15:00:00")
    def test_confirmation_limit_date_has_passed(self, client) -> None:
        booking: Booking = EducationalBookingFactory(
            educationalBooking__confirmationLimitDate=datetime(2021, 8, 5, 14),
            status=BookingStatus.PENDING,
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "CONFIRMATION_LIMIT_DATE_HAS_PASSED"}
