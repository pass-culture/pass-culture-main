from datetime import datetime
import logging

import pytest
import time_machine

from pcapi.core.educational import factories as educational_factories
from pcapi.core.educational.models import CollectiveBooking
import pcapi.core.educational.testing as adage_api_testing
from pcapi.core.educational.utils import get_hashed_user_id
from pcapi.models.offer_mixin import OfferValidationStatus
from pcapi.routes.adage_iframe.serialization.adage_authentication import AdageFrontRoles

from tests.routes.adage_iframe.utils_create_test_token import create_adage_valid_token_with_email


pytestmark = pytest.mark.usefixtures("db_session")

stock_date = datetime(2021, 5, 15)
educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}


class CollectiveBookingTest:
    @time_machine.travel("2020-11-17 15:00:00")
    def test_post_educational_booking(self, client, caplog):
        # Given
        stock = educational_factories.CollectiveStockFactory(startDatetime=stock_date, endDatetime=stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=educational_year_dates["start"], expirationDate=educational_year_dates["end"]
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")

        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # When
        with caplog.at_level(logging.INFO):
            response = client.with_explicit_token(adage_jwt_fake_valid_token).post(
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
        assert caplog.records[0].extra["analyticsSource"] == "adage"
        assert caplog.records[0].extra["stockId"] == stock.id
        assert caplog.records[0].extra["userId"] == get_hashed_user_id(educational_redactor.email)
        assert caplog.records[0].extra["uai"] == educational_institution.institutionId
        assert caplog.records[0].extra["user_role"] == AdageFrontRoles.REDACTOR

        assert len(adage_api_testing.adage_requests) == 1

    @time_machine.travel("2020-11-17 15:00:00")
    def test_post_educational_booking_with_less_redactor_information(self, client):
        # Given
        stock = educational_factories.CollectiveStockFactory(startDatetime=stock_date, endDatetime=stock_date)
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

        # When
        response = client.with_explicit_token(adage_jwt_fake_valid_token).post(
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
        assert educational_redactor.civility is None
        assert educational_redactor.firstName is None
        assert educational_redactor.lastName is None
        assert educational_redactor.email == "new.email@mail.fr"

        assert response.json["bookingId"] == booking.id

        assert len(adage_api_testing.adage_requests) == 1

    @pytest.fixture()
    def test_data(self):
        stock = educational_factories.CollectiveStockFactory(startDatetime=stock_date, endDatetime=stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=educational_year_dates["start"], expirationDate=educational_year_dates["end"]
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        return (stock, educational_institution, educational_redactor)

    def test_should_not_allow_booking_when_educational_institution_is_unknown(self, test_data, client):
        # Given
        stock, _, educational_redactor = test_data
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(
            email=educational_redactor.email, uai="Unknown"
        )

        # When
        response = client.with_explicit_token(adage_jwt_fake_valid_token).post(
            "/adage-iframe/collective/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"code": "UNKNOWN_EDUCATIONAL_INSTITUTION"}
        assert len(adage_api_testing.adage_requests) == 0

    def test_should_not_allow_booking_when_stock_has_no_remaining_quantity(self, test_data, client):
        # Given
        _, educational_institution, educational_redactor = test_data
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=stock_date,
            endDatetime=stock_date,
            collectiveOffer__validation=OfferValidationStatus.REJECTED,
        )
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(
            email=educational_redactor.email, uai=educational_institution.institutionId
        )

        # When
        response = client.with_explicit_token(adage_jwt_fake_valid_token).post(
            "/adage-iframe/collective/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"stock": "Cette offre n'est pas disponible à la réservation"}
        assert len(adage_api_testing.adage_requests) == 0

    def test_should_not_allow_booking_when_uai_code_is_not_provided_through_jwt(self, test_data, client):
        # Given
        stock, _, educational_redactor = test_data
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(email=educational_redactor.email, uai=None)

        # When
        response = client.with_explicit_token(adage_jwt_fake_valid_token).post(
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

    @time_machine.travel("2020-11-17 15:00:00")
    def test_should_not_allow_prebooking_when_uai_code_does_not_match_offer_institution_id(self, client) -> None:
        # Given
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_institution2 = educational_factories.EducationalInstitutionFactory()
        stock = educational_factories.CollectiveStockFactory(
            startDatetime=stock_date,
            endDatetime=stock_date,
            collectiveOffer__institution=educational_institution,
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        educational_factories.EducationalYearFactory(
            beginningDate=educational_year_dates["start"], expirationDate=educational_year_dates["end"]
        )
        adage_jwt_fake_valid_token = create_adage_valid_token_with_email(
            email=educational_redactor.email, uai=educational_institution2.institutionId
        )

        # When
        response = client.with_explicit_token(adage_jwt_fake_valid_token).post(
            "/adage-iframe/collective/bookings",
            json={
                "stockId": stock.id,
            },
        )

        # Then
        assert response.status_code == 403
        assert response.json == {"code": "WRONG_UAI_CODE"}
        assert len(adage_api_testing.adage_requests) == 0
