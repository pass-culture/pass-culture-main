from datetime import datetime
import logging

from freezegun.api import freeze_time
import pytest

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import CollectiveBooking
import pcapi.core.educational.testing as adage_api_testing
from pcapi.core.educational.utils import get_hashed_user_id
from pcapi.models.offer_mixin import OfferValidationStatus

from tests.conftest import TestClient
from tests.routes.adage_iframe.utils_create_test_token import create_adage_valid_token_with_email


pytestmark = pytest.mark.usefixtures("db_session")

stock_date = datetime(2021, 5, 15)
educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}


@freeze_time("2020-11-17 15:00:00")
class Returns200Test:
    def test_post_educational_booking(self, app, caplog):
        # Given
        stock = educational_factories.CollectiveStockFactory(beginningDatetime=stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=educational_year_dates["start"], expirationDate=educational_year_dates["end"]
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")

        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        with caplog.at_level(logging.INFO):
            response = test_client.post(
                "/adage-iframe/collective/bookings",
                json={
                    "stockId": stock.id,
                },
            )

        # Then
        assert response.status_code == 200
        booking = CollectiveBooking.query.filter(CollectiveBooking.collectiveStockId == stock.id).one()
        assert booking.collectiveStock.id == stock.id
        assert booking.educationalInstitution.institutionId == educational_institution.institutionId
        assert booking.educationalYear.adageId == educational_year.adageId
        assert response.json["bookingId"] == booking.id
        assert caplog.records[0].message == "BookingConfirmationButtonClick"
        assert caplog.records[0].extra == {
            "analyticsSource": "adage",
            "stockId": stock.id,
            "userId": get_hashed_user_id(educational_redactor.email),
        }

        assert len(adage_api_testing.adage_requests) == 1

    def test_post_educational_booking_with_less_redactor_information(self, app):
        # Given
        stock = educational_factories.CollectiveStockFactory(beginningDatetime=stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=educational_year_dates["start"], expirationDate=educational_year_dates["end"]
        )

        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(
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
            "/adage-iframe/collective/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 200
        booking = CollectiveBooking.query.filter(CollectiveBooking.collectiveStockId == stock.id).first()
        assert booking.collectiveStock.id == stock.id
        assert booking.educationalInstitution.institutionId == educational_institution.institutionId
        assert booking.educationalYear.adageId == educational_year.adageId
        educational_redactor = booking.educationalRedactor
        assert educational_redactor.civility == None
        assert educational_redactor.firstName == None
        assert educational_redactor.lastName == None
        assert educational_redactor.email == "new.email@mail.fr"

        assert response.json["bookingId"] == booking.id

        assert len(adage_api_testing.adage_requests) == 1


@freeze_time("2020-11-17 15:00:00")
class Returns400Test:
    @pytest.fixture()
    def test_data(self):
        stock = educational_factories.CollectiveStockFactory(beginningDatetime=stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=educational_year_dates["start"], expirationDate=educational_year_dates["end"]
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        return (stock, educational_institution, educational_redactor)

    def test_should_not_allow_booking_when_educational_institution_is_unknown(self, test_data, app):
        # Given
        stock, _, educational_redactor = test_data
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(
            email=educational_redactor.email, uai="Unknown"
        )
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/collective/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"code": "UNKNOWN_EDUCATIONAL_INSTITUTION"}
        assert len(adage_api_testing.adage_requests) == 0

    def test_should_not_allow_booking_when_stock_has_no_remaining_quantity(self, test_data, app):
        # Given
        _, educational_institution, educational_redactor = test_data
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=stock_date, collectiveOffer__validation=OfferValidationStatus.REJECTED
        )
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/collective/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"stock": "Cette offre n'est pas disponible à la réservation"}
        assert len(adage_api_testing.adage_requests) == 0


@freeze_time("2020-11-17 15:00:00")
class Returns403Test:
    @pytest.fixture()
    def test_data(self):
        stock = educational_factories.CollectiveStockFactory(beginningDatetime=stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=educational_year_dates["start"], expirationDate=educational_year_dates["end"]
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        return (stock, educational_institution, educational_redactor)

    def test_should_not_allow_booking_when_uai_code_is_not_provided_through_jwt(self, test_data, app):
        # Given
        stock, _, educational_redactor = test_data
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email=educational_redactor.email, uai=None)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/collective/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 403
        assert response.json == {
            "authorization": "Des informations sur le rédacteur de projet, et nécessaires à la préréservation, sont manquantes"
        }
        assert len(adage_api_testing.adage_requests) == 0

    def test_should_not_allow_prebooking_when_uai_code_does_not_match_offer_institution_id(self, client) -> None:
        # Given
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_institution2 = educational_factories.EducationalInstitutionFactory()
        stock = educational_factories.CollectiveStockFactory(
            beginningDatetime=stock_date, collectiveOffer__institution=educational_institution
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        educational_factories.EducationalYearFactory(
            beginningDate=educational_year_dates["start"], expirationDate=educational_year_dates["end"]
        )
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(
            email=educational_redactor.email, uai=educational_institution2.institutionId
        )
        client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = client.post(
            "/adage-iframe/collective/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 403
        assert response.json == {"code": "WRONG_UAI_CODE"}
        assert len(adage_api_testing.adage_requests) == 0
