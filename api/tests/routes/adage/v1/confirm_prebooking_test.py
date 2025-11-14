import logging
from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from decimal import Decimal

import pytest
import time_machine

from pcapi.core import testing
from pcapi.core.educational import models
from pcapi.core.educational import utils
from pcapi.core.educational.factories import CancelledNotConfirmedCollectiveBookingFactory
from pcapi.core.educational.factories import ConfirmedCollectiveBookingFactory
from pcapi.core.educational.factories import EducationalCurrentYearFactory
from pcapi.core.educational.factories import EducationalDepositFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalRedactorFactory
from pcapi.core.educational.factories import EducationalYearFactory
from pcapi.core.educational.factories import PendingCollectiveBookingFactory
from pcapi.core.educational.factories import create_educational_year
from pcapi.core.offerers.factories import VenueFactory
from pcapi.routes.adage.v1.serialization import constants

from tests.routes.adage.v1.conftest import expected_serialized_prebooking


pytestmark = pytest.mark.usefixtures("db_session")


class Returns200Test:
    # 1. select booking
    # 2. select deposit
    # 3. select stock.price sum
    # 4. update booking
    expected_num_queries = 4

    @time_machine.travel("2021-10-15 09:00:00", tick=False)
    def test_confirm_collective_prebooking(self, client, caplog) -> None:
        redactor = EducationalRedactorFactory()
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        deposit = EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=True,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(20.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalDeposit=deposit,
        )

        booking = PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(20.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalRedactor=redactor,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        booking_id = booking.id
        with caplog.at_level(logging.INFO), testing.assert_num_queries(self.expected_num_queries):
            response = client.post(f"/adage/v1/prebookings/{booking_id}/confirm")

        assert caplog.records[0].message == "BookingApproval"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "bookingId": booking.id,
            "stockId": booking.collectiveStockId,
        }

        assert response.status_code == 200
        assert response.json == expected_serialized_prebooking(booking)

        assert booking.status == models.CollectiveBookingStatus.CONFIRMED
        assert booking.educationalDepositId == deposit.id

    def test_confirm_collective_prebooking_with_address(self, client) -> None:
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory()
        venue = VenueFactory()
        booking = PendingCollectiveBookingFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            collectiveStock__collectiveOffer__venue=venue,
            collectiveStock__collectiveOffer__locationType=models.CollectiveLocationType.ADDRESS,
            collectiveStock__collectiveOffer__offererAddress=venue.offererAddress,
        )
        offer = booking.collectiveStock.collectiveOffer
        deposit = EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=True,
        )

        booking_id = booking.id
        with testing.assert_num_queries(self.expected_num_queries):
            response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking_id}/confirm")

        assert response.status_code == 200
        assert response.json == {
            **expected_serialized_prebooking(booking),
            "address": offer.offererAddress.address.fullAddress,
        }

        assert booking.status == models.CollectiveBookingStatus.CONFIRMED
        assert booking.educationalDepositId == deposit.id

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
        deposit_2 = EducationalDepositFactory(
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            amount=Decimal(10000.00),
            isFinal=True,
        )
        deposit_3 = EducationalDepositFactory(
            educationalInstitution=educational_institution3,
            educationalYear=educational_year,
            amount=Decimal(10000.00),
            isFinal=True,
            ministry=models.Ministry.AGRICULTURE,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(200.00),
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            educationalDeposit=deposit_2,
            confirmationLimitDate=datetime(2021, 10, 21, 10),
        )

        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(200.00),
            educationalInstitution=educational_institution3,
            educationalYear=educational_year,
            educationalDeposit=deposit_3,
            confirmationLimitDate=datetime(2021, 10, 21, 10),
        )

        booking = PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(300.00),
            educationalInstitution=educational_institution3,
            educationalYear=educational_year,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        booking_id = booking.id
        with testing.assert_num_queries(self.expected_num_queries):
            response = client.post(f"/adage/v1/prebookings/{booking_id}/confirm")

        assert response.status_code == 200

        assert booking.status == models.CollectiveBookingStatus.CONFIRMED
        assert booking.educationalDepositId == deposit_3.id

    @time_machine.travel("2021-10-15 09:00:00")
    def test_out_of_minitry_check_dates(self, client) -> None:
        educational_institution = EducationalInstitutionFactory()
        educational_institution2 = EducationalInstitutionFactory()

        educational_year = EducationalYearFactory(adageId="1")
        deposit = EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(2000.00),
            isFinal=True,
        )
        deposit_2 = EducationalDepositFactory(
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            amount=Decimal(10000.00),
            isFinal=True,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(4000.00),
            educationalInstitution=educational_institution2,
            educationalYear=educational_year,
            educationalDeposit=deposit_2,
            confirmationLimitDate=datetime(2021, 10, 21, 10),
        )

        booking = PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(300.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            status=models.CollectiveBookingStatus.PENDING,
            confirmationLimitDate=datetime(2022, 2, 15, 10),
            collectiveStock__startDatetime=datetime(2022, 3, 15, 10),
        )

        client = client.with_eac_token()
        booking_id = booking.id
        with testing.assert_num_queries(self.expected_num_queries):
            response = client.post(f"/adage/v1/prebookings/{booking_id}/confirm")

        assert response.status_code == 200

        assert booking.status == models.CollectiveBookingStatus.CONFIRMED
        assert booking.educationalDepositId == deposit.id

    @pytest.mark.settings(EAC_CHECK_INSTITUTION_FUND=False)
    def test_no_deposit_without_check(self, client):
        booking = PendingCollectiveBookingFactory()

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 200

        assert booking.status == models.CollectiveBookingStatus.CONFIRMED
        assert booking.educationalDepositId is None

    @pytest.mark.settings(EAC_CHECK_INSTITUTION_FUND=False)
    def test_insufficient_fund_without_check(self, client) -> None:
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalCurrentYearFactory()
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(100),
            isFinal=True,
        )
        booking = PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(400),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 200

        assert booking.status == models.CollectiveBookingStatus.CONFIRMED
        assert booking.educationalDepositId is None


class ReturnsErrorTest:
    def test_no_collective_booking(self, client) -> None:
        client = client.with_eac_token()
        response = client.post("/adage/v1/prebookings/404/confirm")

        assert response.status_code == 404
        assert response.json == {"code": constants.EDUCATIONAL_BOOKING_NOT_FOUND}

    @time_machine.travel("2021-10-15 09:00:00")
    def test_no_deposit_for_collective_bookings(self, client) -> None:
        booking = PendingCollectiveBookingFactory(confirmationLimitDate=datetime(2021, 10, 15, 10))

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 404
        assert response.json == {"code": "DEPOSIT_NOT_FOUND"}

        assert booking.status == models.CollectiveBookingStatus.PENDING
        assert booking.educationalDepositId is None

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
        booking = PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_FUND"}

        assert booking.status == models.CollectiveBookingStatus.PENDING
        assert booking.educationalDepositId is None

    @time_machine.travel("2021-10-15 09:00:00")
    def test_insufficient_fund_with_confirmed_booking(self, client) -> None:
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        deposit = EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(100.00),
            isFinal=True,
        )
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(80),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            educationalDeposit=deposit,
        )

        booking = PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(50),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_FUND"}

        assert booking.status == models.CollectiveBookingStatus.PENDING
        assert booking.educationalDepositId is None

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
        booking = PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(400.00),
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            confirmationLimitDate=datetime(2021, 10, 15, 10),
        )

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_FUND_DEPOSIT_NOT_FINAL"}

        assert booking.status == models.CollectiveBookingStatus.PENDING
        assert booking.educationalDepositId is None

    def test_collective_booking_is_cancelled(self, client) -> None:
        booking = CancelledNotConfirmedCollectiveBookingFactory()

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "EDUCATIONAL_BOOKING_IS_CANCELLED"}

        assert booking.status == models.CollectiveBookingStatus.CANCELLED
        assert booking.educationalDepositId is None

    @time_machine.travel("2021-08-05 15:00:00")
    def test_confirmation_limit_date_has_passed_for_collective_bookings(self, client) -> None:
        booking = PendingCollectiveBookingFactory(confirmationLimitDate=datetime(2021, 8, 5, 14))

        client = client.with_eac_token()
        response = client.post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "CONFIRMATION_LIMIT_DATE_HAS_PASSED"}

        assert booking.status == models.CollectiveBookingStatus.PENDING
        assert booking.educationalDepositId is None


time_travel_str_first_period = "2025-10-01 15:00:00"
time_travel_datetime_first_period = datetime.fromisoformat(time_travel_str_first_period)

time_travel_str_second_period = "2026-03-01 15:00:00"
time_travel_datetime_second_period = datetime.fromisoformat(time_travel_str_second_period)


@dataclass
class PeriodData:
    institution: models.EducationalInstitution
    year: models.EducationalYear
    next_year: models.EducationalYear
    deposit_first_period: models.EducationalDeposit
    deposit_second_period: models.EducationalDeposit
    deposit_first_period_next_year: models.EducationalDeposit
    deposit_second_period_next_year: models.EducationalDeposit


def get_period_data() -> PeriodData:
    educational_institution = EducationalInstitutionFactory()
    educational_year = create_educational_year(time_travel_datetime_first_period)
    educational_year_next = create_educational_year(
        time_travel_datetime_first_period.replace(year=time_travel_datetime_first_period.year + 1)
    )

    # one deposit with amount 400 for each period
    deposit_first_period = EducationalDepositFactory(
        educationalYear=educational_year,
        educationalInstitution=educational_institution,
        amount=Decimal(400),
        period=utils.get_educational_year_first_period(educational_year),
    )
    deposit_second_period = EducationalDepositFactory(
        educationalYear=educational_year,
        educationalInstitution=educational_institution,
        amount=Decimal(400),
        period=utils.get_educational_year_second_period(educational_year),
    )
    deposit_first_period_next_year = EducationalDepositFactory(
        educationalYear=educational_year_next,
        educationalInstitution=educational_institution,
        amount=Decimal(400),
        period=utils.get_educational_year_first_period(educational_year_next),
    )
    deposit_second_period_next_year = EducationalDepositFactory(
        educationalYear=educational_year_next,
        educationalInstitution=educational_institution,
        amount=Decimal(400),
        period=utils.get_educational_year_second_period(educational_year_next),
    )

    return PeriodData(
        institution=educational_institution,
        year=educational_year,
        next_year=educational_year_next,
        deposit_first_period=deposit_first_period,
        deposit_second_period=deposit_second_period,
        deposit_first_period_next_year=deposit_first_period_next_year,
        deposit_second_period_next_year=deposit_second_period_next_year,
    )


class PeriodCheckTest:
    @time_machine.travel(time_travel_str_first_period)
    def test_check_deposit_same_period(self, client):
        """
        CASE 1
        Event takes place in first period (september-december)
        Confirmation in first period
        -> period of the deposit is the first period
        """
        period_data = get_period_data()
        # available fund for first period is 400 - 350 = 50
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(350),
            educationalInstitution=period_data.institution,
            educationalYear=period_data.year,
            educationalDeposit=period_data.deposit_first_period,
            collectiveStock__startDatetime=time_travel_datetime_first_period + timedelta(days=5),
        )

        # event takes place in first period and is confirmed now (in first period)
        # -> the deposit is the first period one
        booking = PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(60),
            educationalInstitution=period_data.institution,
            educationalYear=period_data.year,
            collectiveStock__startDatetime=time_travel_datetime_first_period + timedelta(days=5),
        )

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_FUND"}

        assert booking.status == models.CollectiveBookingStatus.PENDING
        assert booking.educationalDepositId is None

        booking.collectiveStock.price = Decimal(40)

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 200

        assert booking.status == models.CollectiveBookingStatus.CONFIRMED
        assert booking.educationalDepositId == period_data.deposit_first_period.id

    @time_machine.travel(time_travel_str_first_period)
    def test_check_deposit_event_in_next_period(self, client):
        """
        CASE 2
        Event takes place in second period (january-august)
        Confirmation in first period (september-december)
        -> period of the deposit is the first period
        """
        period_data = get_period_data()
        # available fund for first period is 400 - 350 = 50
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(350),
            educationalInstitution=period_data.institution,
            educationalYear=period_data.year,
            educationalDeposit=period_data.deposit_first_period,
            collectiveStock__startDatetime=time_travel_datetime_first_period + timedelta(days=5),
        )

        # event takes place in second period and is confirmed now (in first period)
        # -> the deposit is the first period one
        booking = PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(60),
            educationalInstitution=period_data.institution,
            educationalYear=period_data.year,
            collectiveStock__startDatetime=time_travel_datetime_second_period + timedelta(days=5),
        )

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_FUND"}

        assert booking.status == models.CollectiveBookingStatus.PENDING
        assert booking.educationalDepositId is None

        booking.collectiveStock.price = Decimal(40)

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 200

        assert booking.status == models.CollectiveBookingStatus.CONFIRMED
        assert booking.educationalDepositId == period_data.deposit_first_period.id

    @time_machine.travel(time_travel_str_second_period)
    def test_check_deposit_same_period_second(self, client):
        """
        CASE 3
        Event takes place in second period (january-august)
        Confirmation in second period
        -> period of the deposit is the second period
        """
        period_data = get_period_data()
        # available fund for second period is 400 - 350 = 50
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(350),
            educationalInstitution=period_data.institution,
            educationalYear=period_data.year,
            educationalDeposit=period_data.deposit_second_period,
            collectiveStock__startDatetime=time_travel_datetime_second_period + timedelta(days=5),
        )

        # event takes place in second period and is confirmed now (in second period)
        # -> the deposit is the second period one
        booking = PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(60),
            educationalInstitution=period_data.institution,
            educationalYear=period_data.year,
            collectiveStock__startDatetime=time_travel_datetime_second_period + timedelta(days=5),
        )

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_FUND"}

        assert booking.status == models.CollectiveBookingStatus.PENDING
        assert booking.educationalDepositId is None

        booking.collectiveStock.price = Decimal(40)

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 200

        assert booking.status == models.CollectiveBookingStatus.CONFIRMED
        assert booking.educationalDepositId == period_data.deposit_second_period.id

    @time_machine.travel(time_travel_str_second_period)
    def test_check_deposit_event_in_next_year_first_period(self, client):
        """
        CASE 4
        Event takes place in next educational year, first period (september-december)
        Confirmation in current educational year
        -> period of the deposit is the first period of next educational year
        """
        period_data = get_period_data()
        date_in_next_year_first_period = period_data.deposit_first_period_next_year.period.lower + timedelta(days=5)
        # available fund for next year first period is 400 - 350 = 50
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(350),
            educationalInstitution=period_data.institution,
            educationalYear=period_data.next_year,
            educationalDeposit=period_data.deposit_first_period_next_year,
            collectiveStock__startDatetime=date_in_next_year_first_period,
        )

        # event takes place in first period of next educational year and is confirmed now (in current educational year)
        # -> the deposit is the first period of next educational year
        booking = PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(60),
            educationalInstitution=period_data.institution,
            educationalYear=period_data.next_year,
            collectiveStock__startDatetime=date_in_next_year_first_period,
        )

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_FUND"}

        assert booking.status == models.CollectiveBookingStatus.PENDING
        assert booking.educationalDepositId is None

        booking.collectiveStock.price = Decimal(40)

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 200

        assert booking.status == models.CollectiveBookingStatus.CONFIRMED
        assert booking.educationalDepositId == period_data.deposit_first_period_next_year.id

    @time_machine.travel(time_travel_str_second_period)
    def test_check_deposit_event_in_next_year_second_period(self, client):
        """
        CASE 5
        Event takes place in next educational year, second period (january-august)
        Confirmation in current educational year
        -> period of the deposit is the first period of next educational year
        """
        period_data = get_period_data()
        date_in_next_year_first_period = period_data.deposit_first_period_next_year.period.lower + timedelta(days=5)
        date_in_next_year_second_period = period_data.deposit_second_period_next_year.period.lower + timedelta(days=5)

        # available fund for next year first period is 400 - 350 = 50
        ConfirmedCollectiveBookingFactory(
            collectiveStock__price=Decimal(350),
            educationalInstitution=period_data.institution,
            educationalYear=period_data.next_year,
            educationalDeposit=period_data.deposit_first_period_next_year,
            collectiveStock__startDatetime=date_in_next_year_first_period,
        )

        # event takes place in second period of next educational year and is confirmed now (in current educational year)
        # -> the deposit is the first period of next educational year
        booking = PendingCollectiveBookingFactory(
            collectiveStock__price=Decimal(60),
            educationalInstitution=period_data.institution,
            educationalYear=period_data.next_year,
            collectiveStock__startDatetime=date_in_next_year_second_period + timedelta(days=5),
        )

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 422
        assert response.json == {"code": "INSUFFICIENT_FUND"}

        assert booking.status == models.CollectiveBookingStatus.PENDING
        assert booking.educationalDepositId is None

        booking.collectiveStock.price = Decimal(40)

        response = client.with_eac_token().post(f"/adage/v1/prebookings/{booking.id}/confirm")

        assert response.status_code == 200

        assert booking.status == models.CollectiveBookingStatus.CONFIRMED
        assert booking.educationalDepositId == period_data.deposit_first_period_next_year.id
