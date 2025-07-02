from datetime import datetime

import pytest
import time_machine

from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import CollectiveStockFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import UsedCollectiveBookingFactory
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingCancellationReasons
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import CollectiveLocationType
from pcapi.core.educational.models import CollectiveStock
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.testing import assert_num_queries
from pcapi.models import db


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_refuse_collective_booking(self, client):
        redactor = EducationalRedactorFactory(
            civility="M.",
            firstName="Jean",
            lastName="Doudou",
            email="jean.doux@example.com",
        )
        collective_stock: CollectiveStock = CollectiveStockFactory(
            collectiveOffer__bookingEmails=["test_collective@mail.com", "test2_collective@mail.com"],
            startDatetime=datetime(2020, 1, 1, 12, 53, 00),
        )
        collective_booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.PENDING,
            educationalRedactor=redactor,
            collectiveStock=collective_stock,
        )

        client = client.with_eac_token()
        booking_id = collective_booking.id

        num_queries = 1  # re-fetch collective booking with related data
        num_queries += 1  # update booking
        num_queries += 1  # fetch FF (WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE)
        with assert_num_queries(num_queries):
            response = client.post(f"/adage/v1/prebookings/{booking_id}/refuse")

        refused_collective_booking = (
            db.session.query(CollectiveBooking).filter(CollectiveBooking.id == collective_booking.id).first()
        )

        assert response.status_code == 200
        assert refused_collective_booking.status == CollectiveBookingStatus.CANCELLED
        assert (
            refused_collective_booking.cancellationReason == CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE
        )

        collective_offer = collective_stock.collectiveOffer
        educational_institution = refused_collective_booking.educationalInstitution
        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == TransactionalEmail.EDUCATIONAL_BOOKING_CANCELLATION.value.__dict__
        assert mails_testing.outbox[0]["To"] == "test_collective@mail.com"
        assert mails_testing.outbox[0]["Bcc"] == "test2_collective@mail.com"

        assert mails_testing.outbox[0]["params"] == {
            "OFFER_NAME": collective_offer.name,
            "EDUCATIONAL_INSTITUTION_NAME": educational_institution.name,
            "VENUE_NAME": collective_offer.venue.name,
            "EVENT_DATE": "mercredi 1er janvier 2020",
            "EVENT_HOUR": "13h53",
            "REDACTOR_FIRSTNAME": redactor.firstName,
            "REDACTOR_LASTNAME": redactor.lastName,
            "REDACTOR_EMAIL": redactor.email,
            "EDUCATIONAL_INSTITUTION_CITY": educational_institution.city,
            "EDUCATIONAL_INSTITUTION_POSTAL_CODE": educational_institution.postalCode,
            "COLLECTIVE_CANCELLATION_REASON": collective_booking.cancellationReason.value,
            "BOOKING_ID": collective_booking.id,
        }

    @pytest.mark.features(WIP_ENABLE_OFFER_ADDRESS_COLLECTIVE=True)
    def test_refuse_collective_booking_with_oa(self, client):
        collective_booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.PENDING,
            collectiveStock__collectiveOffer__locationType=CollectiveLocationType.ADDRESS,
            collectiveStock__collectiveOffer__offererAddress=None,
            collectiveStock__collectiveOffer__locationComment=None,
        )
        offer = collective_booking.collectiveStock.collectiveOffer
        offer.offererAddress = offer.venue.offererAddress

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{collective_booking.id}/refuse")

        assert response.status_code == 200
        assert response.json["address"] == offer.offererAddress.address.fullAddress

    def test_refuse_collective_booking_when_pending(self, client):
        collective_booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.PENDING,
            cancellationLimitDate=datetime(2020, 1, 1),
            collectiveStock__collectiveOffer__bookingEmails=["johndoe@mail.com", "jacksmith@mail.com"],
        )

        client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{collective_booking.id}/refuse")

        refused_collective_booking = (
            db.session.query(CollectiveBooking).filter(CollectiveBooking.id == collective_booking.id).first()
        )

        assert response.status_code == 200
        assert refused_collective_booking.status == CollectiveBookingStatus.CANCELLED
        assert (
            refused_collective_booking.cancellationReason == CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE
        )
        assert len(mails_testing.outbox) == 1

    @time_machine.travel("2022-11-17 15:00:00")
    def test_refuse_collective_booking_when_confirmed(self, client):
        collective_booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.CONFIRMED,
            cancellationLimitDate=datetime(2022, 11, 18),
            collectiveStock__collectiveOffer__bookingEmails=["johndoe@mail.com", "jacksmith@mail.com"],
        )

        client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{collective_booking.id}/refuse")

        refused_collective_booking = (
            db.session.query(CollectiveBooking).filter(CollectiveBooking.id == collective_booking.id).first()
        )

        assert response.status_code == 200
        assert refused_collective_booking.status == CollectiveBookingStatus.CANCELLED
        assert (
            refused_collective_booking.cancellationReason == CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER
        )
        assert len(mails_testing.outbox) == 1

    @time_machine.travel("2022-05-05 10:00:00")
    def test_returns_no_error_when_already_cancelled(self, client):
        booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.CANCELLED, cancellationLimitDate=datetime(2022, 10, 10)
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/refuse")

        assert response.status_code == 200
        assert len(mails_testing.outbox) == 0


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    def test_returns_error_when_not_refusable(self, client):
        booking = UsedCollectiveBookingFactory()

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/refuse")

        assert response.status_code == 422
        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_REFUSABLE"}
        assert len(mails_testing.outbox) == 0

    def test_returns_error_when_no_educational_booking_found(self, client):
        client = client.with_eac_token()
        response = client.post("/adage/v1/prebookings/123/refuse")

        assert response.status_code == 404
        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_FOUND"}
        assert len(mails_testing.outbox) == 0

    def test_returns_error_when_cancellation_limit_date_is_passed(self, client):
        booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.CONFIRMED,
            cancellationLimitDate=datetime(2020, 1, 1),
        )

        client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/refuse")

        assert response.status_code == 422
        assert response.json == {"code": "EDUCATIONAL_BOOKING_NOT_REFUSABLE"}
        assert len(mails_testing.outbox) == 0
