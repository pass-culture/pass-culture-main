import csv
from datetime import datetime
from io import StringIO

import pytest

from pcapi.core.educational import factories as educational_factories
import pcapi.core.offers.factories as offers_factories

from tests.conftest import TestClient


pytestmark = pytest.mark.usefixtures("db_session")


def reader_from_response(response):
    csv_pseudo_file = StringIO(response.data.decode("utf-8-sig"))
    reader = csv.DictReader(csv_pseudo_file, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
    return list(reader)


class Returns200Test:
    def test_complete_booking_single(self, app):
        user_offerer = offers_factories.UserOffererFactory()
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
            "/collective/bookings/csv?bookingPeriodBeginningDate=2000-01-01&bookingPeriodEndingDate=2030-01-01"
        )

        assert response.status_code == 200
        reader = reader_from_response(response)
        assert len(reader) == 1
        assert reader[0]["Lieu"] == booking.venue.name
        assert reader[0]["Nom de l'offre"] == booking.collectiveStock.collectiveOffer.name
        assert reader[0]["Date de l'évènement"] == "2020-08-13 14:00:00+02:00"
        assert reader[0]["Nom et prénom du bénéficiaire"] == "Kelso Bob"
        assert reader[0]["Email du bénéficiaire"] == booking.educationalRedactor.email
        assert reader[0]["Date et heure de réservation"] == "2020-08-11 14:00:00+02:00"
        assert reader[0]["Date et heure de validation"] == "2020-08-15 14:00:00+02:00"
        assert reader[0]["Prix de la réservation"] == booking.collectiveStock.price
        assert reader[0]["Date et heure de remboursement"] == "2021-08-11 14:00:00+02:00"

    def test_created_booking_single(self, app):
        user_offerer = offers_factories.UserOffererFactory()
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
            "/collective/bookings/csv?bookingPeriodBeginningDate=2000-01-01&bookingPeriodEndingDate=2030-01-01"
        )

        assert response.status_code == 200
        reader = reader_from_response(response)
        assert len(reader) == 1
        assert reader[0]["Lieu"] == booking.venue.name
        assert reader[0]["Nom de l'offre"] == booking.collectiveStock.collectiveOffer.name
        assert reader[0]["Date de l'évènement"] == "2020-08-13 14:00:00+02:00"
        assert reader[0]["Nom et prénom du bénéficiaire"] == "Cox Perry"
        assert reader[0]["Email du bénéficiaire"] == booking.educationalRedactor.email
        assert reader[0]["Date et heure de réservation"] == "2020-08-11 14:00:00+02:00"
        assert reader[0]["Date et heure de validation"] == ""
        assert reader[0]["Prix de la réservation"] == booking.collectiveStock.price
        assert reader[0]["Date et heure de remboursement"] == ""

    def test_one_invisible_rights_booking(self, app):
        invisible_user_offerer = offers_factories.UserOffererFactory()
        educational_factories.CollectiveBookingFactory(
            collectiveStock__collectiveOffer__venue__managingOfferer=invisible_user_offerer.offerer,
            offerer=invisible_user_offerer.offerer,
        )
        user_offerer = offers_factories.UserOffererFactory()
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
            "/collective/bookings/csv?bookingPeriodBeginningDate=2000-01-01&bookingPeriodEndingDate=2030-01-01"
        )

        assert response.status_code == 200
        reader = reader_from_response(response)
        assert len(reader) == 1
        assert reader[0]["Lieu"] == booking.venue.name
        assert reader[0]["Nom de l'offre"] == booking.collectiveStock.collectiveOffer.name
        assert reader[0]["Date de l'évènement"] == "2020-08-13 14:00:00+02:00"
        assert reader[0]["Nom et prénom du bénéficiaire"] == "Dorian John Michael"
        assert reader[0]["Email du bénéficiaire"] == booking.educationalRedactor.email
        assert reader[0]["Date et heure de réservation"] == "2020-08-11 14:00:00+02:00"
        assert reader[0]["Date et heure de validation"] == "2020-08-15 14:00:00+02:00"
        assert reader[0]["Prix de la réservation"] == booking.collectiveStock.price
        assert reader[0]["Date et heure de remboursement"] == "2021-08-11 14:00:00+02:00"

    def test_one_invisible_date_range_booking(self, app):
        invisible_user_offerer = offers_factories.UserOffererFactory()
        educational_factories.CollectiveBookingFactory(
            dateCreated=datetime(2015, 8, 11, 12, 0, 0),
            collectiveStock__collectiveOffer__venue__managingOfferer=invisible_user_offerer.offerer,
            offerer=invisible_user_offerer.offerer,
        )
        user_offerer = offers_factories.UserOffererFactory()
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
            "/collective/bookings/csv?bookingPeriodBeginningDate=2015-01-01&bookingPeriodEndingDate=2030-01-01"
        )

        assert response.status_code == 200
        reader = reader_from_response(response)
        assert len(reader) == 1
        assert reader[0]["Lieu"] == booking.venue.name
        assert reader[0]["Nom de l'offre"] == booking.collectiveStock.collectiveOffer.name
        assert reader[0]["Date de l'évènement"] == "2020-08-13 14:00:00+02:00"
        assert reader[0]["Nom et prénom du bénéficiaire"] == "Reid Eliot"
        assert reader[0]["Email du bénéficiaire"] == booking.educationalRedactor.email
        assert reader[0]["Date et heure de réservation"] == "2020-08-11 14:00:00+02:00"
        assert reader[0]["Date et heure de validation"] == "2020-08-15 14:00:00+02:00"
        assert reader[0]["Prix de la réservation"] == booking.collectiveStock.price
        assert reader[0]["Date et heure de remboursement"] == "2021-08-11 14:00:00+02:00"

    def test_complete_booking_multiple(self, app):
        user_offerer = offers_factories.UserOffererFactory()
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
            "/collective/bookings/csv?bookingPeriodBeginningDate=2000-01-01&bookingPeriodEndingDate=2030-01-01"
        )

        assert response.status_code == 200
        reader = reader_from_response(response)
        assert len(reader) == 3
        for i in range(3):
            name = f"{bookings[i].educationalRedactor.lastName} {bookings[i].educationalRedactor.firstName}"
            assert reader[i]["Lieu"] == bookings[i].venue.name
            assert reader[i]["Nom de l'offre"] == bookings[i].collectiveStock.collectiveOffer.name
            assert reader[i]["Date de l'évènement"] == "2020-08-13 14:00:00+02:00"
            assert reader[i]["Nom et prénom du bénéficiaire"] == name
            assert reader[i]["Email du bénéficiaire"] == bookings[i].educationalRedactor.email
            assert reader[i]["Date et heure de réservation"] == "2020-08-11 14:00:00+02:00"
            assert reader[i]["Date et heure de validation"] == "2020-08-15 14:00:00+02:00"
            assert reader[i]["Prix de la réservation"] == bookings[i].collectiveStock.price
            assert reader[i]["Date et heure de remboursement"] == "2021-08-11 14:00:00+02:00"
