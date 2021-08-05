from decimal import Decimal

import pytest
from sqlalchemy import create_engine
import sqlalchemy.exc
from sqlalchemy.sql import text

from pcapi.core.bookings.factories import EducationalBookingFactory
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.educational import exceptions
from pcapi.core.educational.api import confirm_educational_booking
from pcapi.core.educational.factories import EducationalDepositFactory
from pcapi.core.educational.factories import EducationalInstitutionFactory
from pcapi.core.educational.factories import EducationalYearFactory

from tests.conftest import clean_database


class ConfirmEducationalBookingTest:
    @clean_database
    def test_confirm_educational_booking_lock(self, app):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        deposit = EducationalDepositFactory(
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
            status=BookingStatus.PENDING,
        )

        # open a second connection on purpose and lock the deposit
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        with engine.connect() as connection:
            connection.execute(
                text("""SELECT * FROM educational_deposit WHERE id = :educational_deposit_id FOR UPDATE"""),
                educational_deposit_id=deposit.id,
            )

            with pytest.raises(sqlalchemy.exc.OperationalError):
                confirm_educational_booking(booking.educationalBookingId)

        refreshed_booking = Booking.query.filter(Booking.id == booking.id).one()
        assert refreshed_booking.status == BookingStatus.PENDING

    def test_confirm_educational_booking(self, db_session):
        educational_institution = EducationalInstitutionFactory()
        educational_year = EducationalYearFactory(adageId="1")
        EducationalDepositFactory(
            educationalInstitution=educational_institution,
            educationalYear=educational_year,
            amount=Decimal(1400.00),
            isFinal=True,
        )
        booking = EducationalBookingFactory(
            amount=Decimal(20.00),
            quantity=20,
            educationalBooking__educationalInstitution=educational_institution,
            educationalBooking__educationalYear=educational_year,
            status=BookingStatus.PENDING,
        )
        confirm_educational_booking(booking.educationalBookingId)

        assert booking.status == BookingStatus.CONFIRMED

    def test_raises_if_no_educational_booking(self):
        with pytest.raises(exceptions.EducationalBookingNotFound):
            confirm_educational_booking(100)

    def test_raises_if_no_educational_deposit(self, db_session):
        booking = EducationalBookingFactory(status=BookingStatus.PENDING)
        with pytest.raises(exceptions.EducationalDepositNotFound):
            confirm_educational_booking(booking.educationalBookingId)

    def test_raises_insufficient_fund(self, db_session) -> None:
        # When
        educational_year = EducationalYearFactory(adageId="1")
        educational_institution = EducationalInstitutionFactory()
        EducationalDepositFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            amount=Decimal(400.00),
            isFinal=True,
        )
        booking = EducationalBookingFactory(
            educationalBooking__educationalYear=educational_year,
            educationalBooking__educationalInstitution=educational_institution,
            amount=Decimal(500.00),
            quantity=1,
            status=BookingStatus.PENDING,
        )

        # Then
        with pytest.raises(exceptions.InsufficientFund):
            confirm_educational_booking(booking.educationalBookingId)

    def test_raises_insufficient_temporary_fund(self, db_session) -> None:
        # When
        educational_year = EducationalYearFactory(adageId="1")
        educational_institution = EducationalInstitutionFactory()
        EducationalDepositFactory(
            educationalYear=educational_year,
            educationalInstitution=educational_institution,
            amount=Decimal(1000.00),
            isFinal=False,
        )
        booking = EducationalBookingFactory(
            educationalBooking__educationalYear=educational_year,
            educationalBooking__educationalInstitution=educational_institution,
            amount=Decimal(900.00),
            quantity=1,
            status=BookingStatus.PENDING,
        )

        # Then
        with pytest.raises(exceptions.InsufficientTemporaryFund):
            confirm_educational_booking(booking.educationalBookingId)
