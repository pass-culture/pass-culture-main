from datetime import datetime
from typing import ByteString
from typing import Optional

from freezegun.api import freeze_time
import pytest

from pcapi.core.bookings.models import Booking
from pcapi.core.educational import factories as educational_factories
from pcapi.core.offers import factories as offer_factories

from tests.conftest import TestClient
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


pytestmark = pytest.mark.usefixtures("db_session")

stock_date = datetime(2021, 5, 15)
educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}


def _create_adage_valid_token_with_email(
    email: str,
    civility: Optional[str] = "Mme",
    lastname: Optional[str] = "LAPROF",
    firstname: Optional[str] = "Jeanne",
    uai: Optional[str] = "EAU123",
) -> ByteString:
    return create_adage_jwt_fake_valid_token(
        civility=civility, lastname=lastname, firstname=firstname, email=email, uai=uai
    )


@freeze_time("2020-11-17 15:00:00")
class Returns200Test:
    def test_post_educational_booking(self, app):
        # Given
        stock = offer_factories.EducationalStockFactory(beginningDatetime=stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=educational_year_dates["start"], expirationDate=educational_year_dates["end"]
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")

        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 200
        booking = Booking.query.filter(Booking.stockId == stock.id).first()
        assert booking.educationalBookingId is not None
        assert booking.individualBookingId is None
        assert booking.stock.id == stock.id
        assert booking.educationalBooking.educationalInstitution.institutionId == educational_institution.institutionId
        assert booking.educationalBooking.educationalYear.adageId == educational_year.adageId
        assert response.json["bookingId"] == booking.id

    def test_post_educational_booking_with_less_redactor_information(self, app):
        # Given
        stock = offer_factories.EducationalStockFactory(beginningDatetime=stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=educational_year_dates["start"], expirationDate=educational_year_dates["end"]
        )

        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(
            email="new.email@mail.fr",
            uai=educational_institution.institutionId,
            civility=None,
            firstname=None,
            lastname=None,
        )
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 200
        booking = Booking.query.filter(Booking.stockId == stock.id).first()
        assert booking.educationalBookingId is not None
        assert booking.individualBookingId is None
        assert booking.stock.id == stock.id
        educational_booking = booking.educationalBooking
        assert educational_booking.educationalInstitution.institutionId == educational_institution.institutionId
        assert educational_booking.educationalYear.adageId == educational_year.adageId
        educational_redactor = educational_booking.educationalRedactor
        assert educational_redactor.civility == None
        assert educational_redactor.firstName == None
        assert educational_redactor.lastName == None
        assert educational_redactor.email == "new.email@mail.fr"

        assert response.json["bookingId"] == booking.id


@freeze_time("2020-11-17 15:00:00")
class Returns400Test:
    @pytest.fixture()
    def test_data(self):
        stock = offer_factories.EducationalStockFactory(beginningDatetime=stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=educational_year_dates["start"], expirationDate=educational_year_dates["end"]
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        return (stock, educational_institution, educational_redactor)

    def test_should_not_allow_booking_when_educational_institution_is_unknown(self, test_data, app):
        # Given
        stock, _, educational_redactor = test_data
        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(
            email=educational_redactor.email, uai="Unknown"
        )
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"educationalInstitution": "Cet établissement n'est pas éligible au pass Culture."}

    def test_should_not_allow_booking_when_stock_has_no_remaining_quantity(self, test_data, app):
        # Given
        _, educational_institution, educational_redactor = test_data
        stock = offer_factories.EducationalStockFactory(beginningDatetime=stock_date, quantity=0)
        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"stock": "Cette offre n'est pas disponible à la réservation"}

    def test_should_not_allow_booking_when_offer_is_not_educational(self, test_data, app):
        # Given
        _, educational_institution, educational_redactor = test_data
        stock = offer_factories.EventStockFactory(beginningDatetime=stock_date, offer__isEducational=False)
        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"offer": "L'offre n'est pas une offre éducationnelle"}

    def test_should_not_allow_booking_when_educational_offer_is_not_an_event(self, test_data, app):
        # Given
        _, educational_institution, educational_redactor = test_data
        stock = offer_factories.ThingStockFactory(offer__isEducational=True, beginningDatetime=stock_date)
        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"offer": "L'offre n'est pas un évènement"}


@freeze_time("2020-11-17 15:00:00")
class Returns403Test:
    @pytest.fixture()
    def test_data(self):
        stock = offer_factories.EducationalStockFactory(beginningDatetime=stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=educational_year_dates["start"], expirationDate=educational_year_dates["end"]
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        return (stock, educational_institution, educational_redactor)

    def test_should_not_allow_booking_when_uai_code_is_not_provided_through_jwt(self, test_data, app):
        # Given
        stock, _, educational_redactor = test_data
        adage_jwt_fake_valid_token = _create_adage_valid_token_with_email(email=educational_redactor.email, uai=None)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 403
        assert response.json == {
            "authorization": "Des informations sur le rédacteur de projet, et nécessaires à la préréservation, sont manquantes"
        }
