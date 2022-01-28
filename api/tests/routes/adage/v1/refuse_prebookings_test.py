from datetime import datetime

from freezegun import freeze_time
import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.models import EducationalBookingStatus
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.factories import EventStockFactory
from pcapi.core.offers.models import Stock
from pcapi.core.offers.utils import offer_app_link
from pcapi.core.testing import override_features
from pcapi.utils.date import format_into_utc_date

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @freeze_time("2022-11-17 15:00:00")
    @override_features(ENABLE_SENDINBLUE_TRANSACTIONAL_EMAILS=True)
    def test_refuse_educational_booking(
        self,
        app,
    ) -> None:
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        stock: Stock = EventStockFactory(
            quantity=200,
            dnBookedQuantity=0,
            offer__bookingEmail="test@mail.com",
            beginningDatetime=datetime(2020, 1, 1, 12, 53, 00),
        )
        booking = EducationalBookingFactory(
            educationalBooking__educationalRedactor=redactor,
            status=BookingStatus.CONFIRMED,
            stock=stock,
            quantity=20,
            cancellation_limit_date=datetime(2023, 1, 1),
            dateCreated=datetime(2021, 12, 15, 10, 5, 5),
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
            "address": f"{venue.address}, {venue.postalCode} {venue.city}",
            "accessibility": "Non accessible",
            "beginningDatetime": format_into_utc_date(stock.beginningDatetime),
            "cancellationDate": "2022-11-17T15:00:00Z",
            "cancellationLimitDate": format_into_utc_date(booking.cancellationLimitDate),
            "city": venue.city,
            "confirmationDate": None,
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
            "numberOfTickets": None,
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
            "status": "REFUSED",
            "subcategoryLabel": "Séance de cinéma",
            "venueTimezone": venue.timezone,
            "totalAmount": booking.total_amount,
            "url": offer_app_link(offer),
            "withdrawalDetails": offer.withdrawalDetails,
        }

        # It should be 0 because on booking factory creation it goes to 20, then on cancellation it goes 20-20
        assert stock.dnBookedQuantity == 0
        assert booking.status == BookingStatus.CANCELLED
        assert booking.cancellationReason == BookingCancellationReasons.REFUSED_BY_INSTITUTE

        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.EDUCATIONAL_BOOKING_CANCELLATION_BY_INSTITUTION.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == "test@mail.com"
        assert mails_testing.outbox[0].sent_data["params"] == {
            "OFFER_NAME": offer.name,
            "EVENT_BEGINNING_DATETIME": "01/01/2020 à 12:53",
            "EDUCATIONAL_REDACTOR_EMAIL": "jean.doux@example.com",
        }

    def test_refuse_educational_booking_when_pending(self, client) -> None:
        booking = EducationalBookingFactory(
            status=BookingStatus.PENDING,
            cancellationLimitDate=datetime(2020, 1, 1),
        )

        client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/refuse")

        assert response.status_code == 200


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

    def test_returns_error_when_cancellation_limit_date_is_passed(self, client) -> None:
        booking = EducationalBookingFactory(
            status=BookingStatus.CONFIRMED,
            cancellation_limit_date=datetime(2020, 1, 1),
        )

        client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/refuse")

        assert response.status_code == 422

        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_REFUSABLE"}
