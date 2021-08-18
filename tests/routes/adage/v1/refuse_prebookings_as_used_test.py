from freezegun import freeze_time
import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.models import EducationalBookingStatus
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.models import Stock
from pcapi.core.offers.utils import offer_webapp_link
from pcapi.routes.native.v1.serialization.offers import get_serialized_offer_category
from pcapi.utils.date import format_into_utc_date

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @freeze_time("2022-11-17 15:00:00")
    def test_refuse_prebooking(self, app) -> None:
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        stock: Stock = EventStockFactory(quantity=200, dnBookedQuantity=0)
        booking = EducationalBookingFactory(
            educationalBooking__educationalRedactor=redactor,
            status=BookingStatus.CONFIRMED,
            stock=stock,
            quantity=20,
        )

        client = TestClient(app.test_client()).with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/refuse")

        assert response.status_code == 200

        booking = Booking.query.one()
        stock = booking.stock
        offer = stock.offer
        venue = offer.venue
        educational_booking = booking.educationalBooking
        assert response.json == {
            "address": venue.address,
            "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
            "cancellationDate": "2022-11-17T15:00:00Z",
            "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
            "category": get_serialized_offer_category(offer),
            "city": venue.city,
            "confirmationDate": None,
            "confirmationLimitDate": format_into_utc_date(educational_booking.confirmationLimitDate),
            "coordinates": {
                "latitude": float(venue.latitude),
                "longitude": float(venue.longitude),
            },
            "creationDate": format_into_utc_date(booking.dateCreated),
            "description": offer.description,
            "durationMinutes": offer.durationMinutes,
            "expirationDate": booking.expirationDate,
            "id": educational_booking.id,
            "image": None,
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
            "status": "REFUSED",
            "venueTimezone": venue.timezone,
            "totalAmount": booking.total_amount,
            "url": offer_webapp_link(offer),
            "withdrawalDetails": offer.withdrawalDetails,
        }

        # It should be 0 because on booking factory creation it goes to 20, then on cancellation it goes 20-20
        assert stock.dnBookedQuantity == 0
        assert booking.status == BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.REFUSED_BY_INSTITUTE


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_returns_error_when_not_refusable(self, app) -> None:
        booking = EducationalBookingFactory(
            educationalBooking__status=EducationalBookingStatus.USED_BY_INSTITUTE,
        )

        client = TestClient(app.test_client()).with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/refuse")

        assert response.status_code == 422

        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_REFUSABLE"}

    def test_returns_error_when_already_cancelled(self, app) -> None:
        booking = EducationalBookingFactory(
            status=BookingStatus.CANCELLED,
        )

        client = TestClient(app.test_client()).with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/refuse")

        assert response.status_code == 422

        assert response.json == {"code": "EDUCATIONAL_BOOKING_ALREADY_CANCELLED"}

    def test_returns_error_when_no_educational_booking_found(self, app) -> None:
        client = TestClient(app.test_client()).with_eac_token()
        response = client.post("/adage/v1/prebookings/123/refuse")

        assert response.status_code == 404

        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_FOUND"}
