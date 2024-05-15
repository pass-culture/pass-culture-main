from datetime import datetime
from decimal import Decimal
import logging

import pytest
import time_machine

from pcapi.core.bookings.models import Booking
from pcapi.core.educational.factories import CollectiveBookingFactory
from pcapi.core.educational.factories import EducationalDepositFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.models import CollectiveBooking
from pcapi.core.educational.models import CollectiveBookingStatus
from pcapi.core.educational.models import Ministry
from pcapi.core.testing import override_features
from pcapi.routes.adage.v1.serialization import constants

from tests.routes.adage.v1.conftest import expected_serialized_prebooking


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    @time_machine.travel("2021-10-15 09:00:00", tick=False)
    def test_confirm_collective_prebooking(self, client, caplog) -> None:
        redactor = EducationalRedactorFactory()
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
        with caplog.at_level(logging.INFO):
            response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert caplog.records[0].message == "BookingApproval"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "bookingId": booking.id,
            "stockId": booking.collectiveStockId,
        }

        assert response.status_code == 200
        assert response.json == expected_serialized_prebooking(booking)
        assert (
            CollectiveBooking.query.filter(CollectiveBooking.id == booking.id).one().status
            == CollectiveBookingStatus.CONFIRMED
        )

    @time_machine.travel("2021-10-15 09:00:00")
    @override_features(ENABLE_EAC_FINANCIAL_PROTECTION=True)
    def test_insufficient_ministry_fund_other_ministry(self, client) -> None:
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

    @time_machine.travel("2021-10-15 09:00:00")
    def test_sufficient_ministry_fund(self, client) -> None:
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

    @time_machine.travel("2021-10-15 09:00:00")
    def test_out_of_minitry_check_dates(self, client) -> None:
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
            collectiveStock__startDatetime=datetime(2022, 3, 15, 10),
            collectiveStock__endDatetime=datetime(2022, 3, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")
        assert response.status_code == 200


class ReturnsErrorTest:
    def test_no_educational_booking(self, client) -> None:
        client = client.with_eac_token()
        response = client.post("/adage/v1/prebookings/404/confirm")

        assert response.status_code == 404
        assert response.json == {"code": constants.EDUCATIONAL_BOOKING_NOT_FOUND}

    def test_no_collective_booking(self, client) -> None:
        client = client.with_eac_token()
        response = client.post("/adage/v1/prebookings/404/confirm")

        assert response.status_code == 404
        assert response.json == {"code": constants.EDUCATIONAL_BOOKING_NOT_FOUND}

    @time_machine.travel("2021-10-15 09:00:00")
    def test_no_deposit_for_collective_bookings(self, client) -> None:
        booking = CollectiveBookingFactory(
            collectiveStock__price=Decimal(20.00),
            status=CollectiveBookingStatus.PENDING,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 404
        assert response.json == {"code": "DEPOSIT_NOT_FOUND"}

    @time_machine.travel("2021-10-15 09:00:00")
    def test_insufficient_fund_for_collective_bookings(self, client) -> None:
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

    @time_machine.travel("2021-10-15 09:00:00")
    @override_features(ENABLE_EAC_FINANCIAL_PROTECTION=True)
    def test_insufficient_ministry_fund_for_collective_bookings(self, client) -> None:
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

    @time_machine.travel("2021-10-15 09:00:00")
    def test_insufficient_temporary_fund_for_collective_bookings(self, client) -> None:
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

    def test_collective_booking_is_cancelled(self, client) -> None:
        booking = CollectiveBookingFactory(
            status=CollectiveBookingStatus.CANCELLED,
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "EDUCATIONAL_BOOKING_IS_CANCELLED"}

    @time_machine.travel("2021-08-05 15:00:00")
    def test_confirmation_limit_date_has_passed_for_collective_bookings(self, client) -> None:
        booking: Booking = CollectiveBookingFactory(
            confirmationLimitDate=datetime(2021, 8, 5, 14),
            status=CollectiveBookingStatus.PENDING,
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "CONFIRMATION_LIMIT_DATE_HAS_PASSED"}
