from datetime import datetime
from io import BytesIO

import openpyxl
import pytest

from pcapi.core.educational import factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.routes.serialization.collective_bookings_serialize import COLLECTIVE_BOOKING_EXPORT_HEADER

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


def reader_from_response(response):
    wb = openpyxl.load_workbook(BytesIO(response.data))
    return wb.active


class Returns200Test:
    def test_complete_booking_single(self, app):
        user_offerer = offerers_factories.UserOffererFactory()
        booking = educational_factories.CollectiveBookingFactory(
            dateCreated=datetime(2020, 8, 11, 12, 0, 0),
            collectiveStock__beginningDatetime=datetime(2020, 8, 13, 12, 0, 0),
            reimbursementDate=datetime(2021, 8, 11, 12, 0, 0),
            dateUsed=datetime(2020, 8, 15, 12, 0, 0),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            offerer=user_offerer.offerer,
            educationalRedactor__firstName="Bob",
            educationalRedactor__lastName="Kelso",
        )

        client = TestClient(app.test_client()).with_session_auth(user_offerer.user.email)
        response = client.get(
            "/collective/bookings/excel?bookingPeriodBeginningDate=2000-01-01&bookingPeriodEndingDate=2030-01-01"
        )

        assert response.status_code == 200
        sheet = reader_from_response(response)
        # Headers
        for i in range(1, len(COLLECTIVE_BOOKING_EXPORT_HEADER)):
            assert sheet.cell(row=1, column=i).value == COLLECTIVE_BOOKING_EXPORT_HEADER[i - 1]
        # Celles
        assert sheet.cell(row=2, column=1).value == booking.venue.name
        assert sheet.cell(row=2, column=2).value == booking.collectiveStock.collectiveOffer.name
        assert sheet.cell(row=2, column=3).value == "2020-08-13 14:00:00+02:00"
        assert sheet.cell(row=2, column=4).value == "Kelso Bob"
        assert sheet.cell(row=2, column=5).value == booking.educationalRedactor.email
        assert sheet.cell(row=2, column=6).value == "2020-08-11 14:00:00+02:00"
        assert sheet.cell(row=2, column=7).value == "2020-08-15 14:00:00+02:00"
        assert sheet.cell(row=2, column=8).value == booking.collectiveStock.price
        assert sheet.cell(row=2, column=9).value == "2021-08-11 14:00:00+02:00"

    def test_created_booking_single(self, app):
        user_offerer = offerers_factories.UserOffererFactory()
        booking = educational_factories.CollectiveBookingFactory(
            dateCreated=datetime(2020, 8, 11, 12, 0, 0),
            collectiveStock__beginningDatetime=datetime(2020, 8, 13, 12, 0, 0),
            reimbursementDate=None,
            dateUsed=None,
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            offerer=user_offerer.offerer,
            educationalRedactor__firstName="Perry",
            educationalRedactor__lastName="Cox",
        )

        client = TestClient(app.test_client()).with_session_auth(user_offerer.user.email)
        response = client.get(
            "/collective/bookings/excel?bookingPeriodBeginningDate=2000-01-01&bookingPeriodEndingDate=2030-01-01"
        )

        assert response.status_code == 200
        sheet = reader_from_response(response)
        # Headers
        for i in range(1, len(COLLECTIVE_BOOKING_EXPORT_HEADER)):
            assert sheet.cell(row=1, column=i).value == COLLECTIVE_BOOKING_EXPORT_HEADER[i - 1]
        # Cells
        assert sheet.cell(row=2, column=1).value == booking.venue.name
        assert sheet.cell(row=2, column=2).value == booking.collectiveStock.collectiveOffer.name
        assert sheet.cell(row=2, column=3).value == "2020-08-13 14:00:00+02:00"
        assert sheet.cell(row=2, column=4).value == "Cox Perry"
        assert sheet.cell(row=2, column=5).value == booking.educationalRedactor.email
        assert sheet.cell(row=2, column=6).value == "2020-08-11 14:00:00+02:00"
        assert sheet.cell(row=2, column=7).value == "None"
        assert sheet.cell(row=2, column=8).value == booking.collectiveStock.price
        assert sheet.cell(row=2, column=9).value == "None"

    def test_one_invisible_rights_booking(self, app):
        invisible_user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=invisible_user_offerer.offerer,
            offerer=invisible_user_offerer.offerer,
        )
        user_offerer = offerers_factories.UserOffererFactory()
        booking = educational_factories.CollectiveBookingFactory(
            dateCreated=datetime(2020, 8, 11, 12, 0, 0),
            collectiveStock__beginningDatetime=datetime(2020, 8, 13, 12, 0, 0),
            reimbursementDate=datetime(2021, 8, 11, 12, 0, 0),
            dateUsed=datetime(2020, 8, 15, 12, 0, 0),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            offerer=user_offerer.offerer,
            educationalRedactor__firstName="John Michael",
            educationalRedactor__lastName="Dorian",
        )

        client = TestClient(app.test_client()).with_session_auth(user_offerer.user.email)
        response = client.get(
            "/collective/bookings/excel?bookingPeriodBeginningDate=2000-01-01&bookingPeriodEndingDate=2030-01-01"
        )

        assert response.status_code == 200
        sheet = reader_from_response(response)
        # Headers
        for i in range(1, len(COLLECTIVE_BOOKING_EXPORT_HEADER)):
            assert sheet.cell(row=1, column=i).value == COLLECTIVE_BOOKING_EXPORT_HEADER[i - 1]
        # Cells
        assert sheet.cell(row=2, column=1).value == booking.venue.name
        assert sheet.cell(row=2, column=2).value == booking.collectiveStock.collectiveOffer.name
        assert sheet.cell(row=2, column=3).value == "2020-08-13 14:00:00+02:00"
        assert sheet.cell(row=2, column=4).value == "Dorian John Michael"
        assert sheet.cell(row=2, column=5).value == booking.educationalRedactor.email
        assert sheet.cell(row=2, column=6).value == "2020-08-11 14:00:00+02:00"
        assert sheet.cell(row=2, column=7).value == "2020-08-15 14:00:00+02:00"
        assert sheet.cell(row=2, column=8).value == booking.collectiveStock.price
        assert sheet.cell(row=2, column=9).value == "2021-08-11 14:00:00+02:00"

        for i in range(1, len(COLLECTIVE_BOOKING_EXPORT_HEADER)):
            assert sheet.cell(row=3, column=i).value == None

    def test_one_invisible_date_range_booking(self, app):
        invisible_user_offerer = offerers_factories.UserOffererFactory()
        educational_factories.CollectiveBookingFactory(
            dateCreated=datetime(2015, 8, 11, 12, 0, 0),
            collectiveStock__collectiveOffer__venue__managingOfferer=invisible_user_offerer.offerer,
            offerer=invisible_user_offerer.offerer,
        )
        user_offerer = offerers_factories.UserOffererFactory()
        booking = educational_factories.CollectiveBookingFactory(
            dateCreated=datetime(2020, 8, 11, 12, 0, 0),
            collectiveStock__beginningDatetime=datetime(2020, 8, 13, 12, 0, 0),
            reimbursementDate=datetime(2021, 8, 11, 12, 0, 0),
            dateUsed=datetime(2020, 8, 15, 12, 0, 0),
            collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
            offerer=user_offerer.offerer,
            educationalRedactor__firstName="Eliot",
            educationalRedactor__lastName="Reid",
        )

        client = TestClient(app.test_client()).with_session_auth(user_offerer.user.email)
        response = client.get(
            "/collective/bookings/excel?bookingPeriodBeginningDate=2015-01-01&bookingPeriodEndingDate=2030-01-01"
        )

        assert response.status_code == 200
        sheet = reader_from_response(response)
        # Headers
        for i in range(1, len(COLLECTIVE_BOOKING_EXPORT_HEADER)):
            assert sheet.cell(row=1, column=i).value == COLLECTIVE_BOOKING_EXPORT_HEADER[i - 1]
        # Cells
        assert sheet.cell(row=2, column=1).value == booking.venue.name
        assert sheet.cell(row=2, column=2).value == booking.collectiveStock.collectiveOffer.name
        assert sheet.cell(row=2, column=3).value == "2020-08-13 14:00:00+02:00"
        assert sheet.cell(row=2, column=4).value == "Reid Eliot"
        assert sheet.cell(row=2, column=5).value == booking.educationalRedactor.email
        assert sheet.cell(row=2, column=6).value == "2020-08-11 14:00:00+02:00"
        assert sheet.cell(row=2, column=7).value == "2020-08-15 14:00:00+02:00"
        assert sheet.cell(row=2, column=8).value == booking.collectiveStock.price
        assert sheet.cell(row=2, column=9).value == "2021-08-11 14:00:00+02:00"

    def test_complete_booking_multiple(self, app):
        user_offerer = offerers_factories.UserOffererFactory()
        bookings = [
            educational_factories.CollectiveBookingFactory(
                dateCreated=datetime(2020, 8, 11, 12, 0, 0),
                collectiveStock__beginningDatetime=datetime(2020, 8, 13, 12, 0, 0),
                reimbursementDate=datetime(2021, 8, 11, 12, 0, 0),
                dateUsed=datetime(2020, 8, 15, 12, 0, 0),
                collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
                offerer=user_offerer.offerer,
                educationalRedactor__firstName="Carla",
                educationalRedactor__lastName="Espinosa",
            ),
            educational_factories.CollectiveBookingFactory(
                dateCreated=datetime(2020, 8, 11, 12, 0, 0),
                collectiveStock__beginningDatetime=datetime(2020, 8, 13, 12, 0, 0),
                reimbursementDate=datetime(2021, 8, 11, 12, 0, 0),
                dateUsed=datetime(2020, 8, 15, 12, 0, 0),
                collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
                offerer=user_offerer.offerer,
                educationalRedactor__firstName="Janitor",
                educationalRedactor__lastName="The",
            ),
            educational_factories.CollectiveBookingFactory(
                dateCreated=datetime(2020, 8, 11, 12, 0, 0),
                collectiveStock__beginningDatetime=datetime(2020, 8, 13, 12, 0, 0),
                reimbursementDate=datetime(2021, 8, 11, 12, 0, 0),
                dateUsed=datetime(2020, 8, 15, 12, 0, 0),
                collectiveStock__collectiveOffer__venue__managingOfferer=user_offerer.offerer,
                offerer=user_offerer.offerer,
                educationalRedactor__firstName="Ted",
                educationalRedactor__lastName="Buckland",
            ),
        ]

        client = TestClient(app.test_client()).with_session_auth(user_offerer.user.email)
        response = client.get(
            "/collective/bookings/excel?bookingPeriodBeginningDate=2000-01-01&bookingPeriodEndingDate=2030-01-01"
        )

        assert response.status_code == 200
        sheet = reader_from_response(response)
        for i in range(2, 5):
            name = f"{bookings[i-2].educationalRedactor.lastName} {bookings[i-2].educationalRedactor.firstName}"
            assert sheet.cell(row=i, column=1).value == bookings[i - 2].venue.name
            assert sheet.cell(row=i, column=2).value == bookings[i - 2].collectiveStock.collectiveOffer.name
            assert sheet.cell(row=i, column=3).value == "2020-08-13 14:00:00+02:00"
            assert sheet.cell(row=i, column=4).value == name
            assert sheet.cell(row=i, column=5).value == bookings[i - 2].educationalRedactor.email
            assert sheet.cell(row=i, column=6).value == "2020-08-11 14:00:00+02:00"
            assert sheet.cell(row=i, column=7).value == "2020-08-15 14:00:00+02:00"
            assert sheet.cell(row=i, column=8).value == bookings[i - 2].collectiveStock.price
            assert sheet.cell(row=i, column=9).value == "2021-08-11 14:00:00+02:00"
