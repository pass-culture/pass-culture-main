from datetime import datetime
from typing import Any

from freezegun import freeze_time
import pytest

from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveStock
import pcapi.core.mails.testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.testing import override_features


@pytest.mark.usefixtures("db_session")
@freeze_time("2022-11-17 15:00:00")
class Returns200Test:
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
        collective_booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.PENDING,
            cancellationLimitDate=datetime(2020, 1, 1),
            collectiveStock__collectiveOffer__bookingEmail="johndoe@mail.com",
        )

        client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{collective_booking.id}/refuse")

        refused_collective_booking = CollectiveBooking.query.filter(
            CollectiveBooking.id == collective_booking.id
        ).first()

        assert response.status_code == 200
        assert refused_collective_booking.status == CollectiveBookingStatus.CANCELLED
        assert len(mails_testing.outbox) == 1

    @freeze_time("2022-05-05 10:00:00")
    def test_returns_no_error_when_already_cancelled(self, client: Any) -> None:
        booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.CANCELLED, cancellationLimitDate=datetime(2022, 10, 10)
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/refuse")

        assert response.status_code == 200
        assert len(mails_testing.outbox) == 0


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_returns_error_when_not_refusable(self, client: Any) -> None:
        booking = UsedCollectiveBookingFactory()

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/refuse")

        assert response.status_code == 422
        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_REFUSABLE"}
        assert len(mails_testing.outbox) == 0

    def test_returns_error_when_no_educational_booking_found(self, client: Any) -> None:
        client = client.with_eac_token()
        response = client.post("/adage/v1/prebookings/123/refuse")

        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_FOUND"}
        assert len(mails_testing.outbox) == 0

    def test_returns_error_when_cancellation_limit_date_is_passed(self, client: Any) -> None:
        booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.CONFIRMED,
            cancellationLimitDate=datetime(2020, 1, 1),
        )

        client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/refuse")

        assert response.status_code == 422
        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_REFUSABLE"}
        assert len(mails_testing.outbox) == 0
