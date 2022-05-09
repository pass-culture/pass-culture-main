from datetime import datetime
from typing import Any
from typing import cast

from freezegun import freeze_time
import pytest

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingCancellationReasons
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offers.factories import EducationalEventStockFactory
from pcapi.core.offers.models import Stock
from pcapi.core.offers.utils import offer_app_link
from pcapi.core.testing import override_features
from pcapi.utils.date import format_into_utc_date


@pytest.mark.usefixtures("db_session")
@freeze_time("2022-11-17 15:00:00")
class Returns200Test:
    def test_refuse_educational_booking(
        self,
        client: Any,
    ) -> None:
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        institution = EducationalInstitutionFactory(name="Collège Dupont", city="Tourcoing", postalCode=59200)
        stock: Stock = EducationalEventStockFactory(
            quantity=200,
            dnBookedQuantity=0,
            offer__bookingEmail="test@mail.com",
            beginningDatetime=datetime(2020, 1, 1, 12, 53, 00),
        )
        booking = EducationalBookingFactory(
            educationalBooking__educationalRedactor=redactor,
            educationalBooking__educationalInstitution=institution,
            status=BookingStatus.CONFIRMED,
            stock=stock,
            quantity=20,
            cancellation_limit_date=datetime(2023, 1, 1),
            dateCreated=datetime(2021, 12, 15, 10, 5, 5),
        )

        client = client.with_eac_token()
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
            "beginningDatetime": format_into_utc_date(cast(datetime, stock.beginningDatetime)),
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
            "numberOfTickets": stock.numberOfTickets,
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
            "EDUCATIONAL_INSTITUTION_NAME": institution.name,
            "VENUE_NAME": venue.name,
            "EVENT_DATE": "01/01/2020",
            "EVENT_HOUR": "12:53",
            "REDACTOR_FIRSTNAME": redactor.firstName,
            "REDACTOR_LASTNAME": redactor.lastName,
            "REDACTOR_EMAIL": redactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": institution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": institution.postalCode,
        }

    def test_refuse_educational_booking_when_pending(self, client: Any) -> None:
        booking = EducationalBookingFactory(
            status=BookingStatus.PENDING,
            cancellationLimitDate=datetime(2020, 1, 1),
        )

        client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/refuse")

        assert response.status_code == 200

    @override_features(ENABLE_NEW_COLLECTIVE_MODEL=True)
    def test_refuse_collective_booking(
        self,
        client: Any,
    ) -> None:
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        collective_stock: CollectiveStock = CollectiveStockFactory(
            collectiveOffer__bookingEmail="test_collective@mail.com",
            beginningDatetime=datetime(2020, 1, 1, 12, 53, 00),
        )
        collective_booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.PENDING,
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{collective_booking.id}/refuse")

        refused_collective_booking = CollectiveBooking.query.filter(
            CollectiveBooking.id == collective_booking.id
        ).first()

        assert response.status_code == 200
        assert refused_collective_booking.status == CollectiveBookingStatus.CANCELLED
        assert (
            refused_collective_booking.cancellationReason == CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE
        )

        collective_offer = collective_stock.collectiveOffer
        educational_institution = refused_collective_booking.educationalInstitution
        assert len(mails_testing.outbox) == 1
        assert (
            mails_testing.outbox[0].sent_data["template"]
            == TransactionalEmail.EDUCATIONAL_BOOKING_CANCELLATION_BY_INSTITUTION.value.__dict__
        )
        assert mails_testing.outbox[0].sent_data["To"] == "test_collective@mail.com"
        assert mails_testing.outbox[0].sent_data["params"] == {
            "OFFER_NAME": collective_offer.name,
            "EDUCATIONAL_INSTITUTION_NAME": educational_institution.name,
            "VENUE_NAME": collective_offer.venue.name,
            "EVENT_DATE": "01/01/2020",
            "EVENT_HOUR": "12:53",
            "REDACTOR_FIRSTNAME": redactor.firstName,
            "REDACTOR_LASTNAME": redactor.lastName,
            "REDACTOR_EMAIL": redactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": educational_institution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": educational_institution.postalCode,
        }

    def test_refuse_collective_booking_when_pending(self, client: Any) -> None:
        booking = EducationalBookingFactory(
            status=BookingStatus.PENDING,
            cancellationLimitDate=datetime(2020, 1, 1),
        )
        collective_booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.PENDING,
            bookingId=booking.id,
        )

        client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/refuse")

        refused_collective_booking = CollectiveBooking.query.filter(
            CollectiveBooking.id == collective_booking.id
        ).first()

        assert response.status_code == 200
        assert refused_collective_booking.status == CollectiveBookingStatus.CANCELLED
        assert len(mails_testing.outbox) == 0


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_returns_error_when_not_refusable(self, client: Any) -> None:
        booking = EducationalBookingFactory(
            status=BookingStatus.USED,
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/refuse")

        assert response.status_code == 422
        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_REFUSABLE"}
        assert len(mails_testing.outbox) == 0

    def test_returns_error_when_already_cancelled(self, client: Any) -> None:
        booking = EducationalBookingFactory(
            status=BookingStatus.CANCELLED,
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/refuse")

        assert response.status_code == 422
        assert response.json == {"code": "EDUCATIONAL_BOOKING_ALREADY_CANCELLED"}
        assert len(mails_testing.outbox) == 0

    def test_returns_error_when_no_educational_booking_found(self, client: Any) -> None:
        client = client.with_eac_token()
        response = client.post("/adage/v1/prebookings/123/refuse")

        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_FOUND"}
        assert len(mails_testing.outbox) == 0

    def test_returns_error_when_cancellation_limit_date_is_passed(self, client: Any) -> None:
        booking = EducationalBookingFactory(
            status=BookingStatus.CONFIRMED,
            cancellation_limit_date=datetime(2020, 1, 1),
        )

        client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.educationalBookingId}/refuse")

        assert response.status_code == 422
        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_REFUSABLE"}
        assert len(mails_testing.outbox) == 0
