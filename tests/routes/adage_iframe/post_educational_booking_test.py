from datetime import datetime

import pytest

from pcapi.core.bookings.models import Booking
from pcapi.core.educational import factories as educational_factories
from pcapi.core.offers import factories as offer_factories

from tests.conftest import TestClient
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


pytestmark = pytest.mark.usefixtures("db_session")


class PostEducationalBookingTest:
    stock_date = datetime(2021, 5, 15)
    educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}

    def test_post_educational_booking(self, app):
        # Given
        stock = offer_factories.EventStockFactory(offer__isEducational=True, beginningDatetime=self.stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=self.educational_year_dates["start"], expirationDate=self.educational_year_dates["end"]
        )
        redactor_email = "professeur.lycee@example.com"

        adage_jwt_fake_valid_token = create_adage_jwt_fake_valid_token(user_email=redactor_email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "redactorEmail": redactor_email,
                "stockId": stock.id,
                "UAICode": educational_institution.institutionId,
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

    def test_should_not_allow_booking_when_educational_institution_is_unknown(self, app):
        # Given
        stock = offer_factories.EventStockFactory(offer__isEducational=True, beginningDatetime=self.stock_date)
        educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=self.educational_year_dates["start"], expirationDate=self.educational_year_dates["end"]
        )
        redactor_email = "professeur.lycee@example.com"

        adage_jwt_fake_valid_token = create_adage_jwt_fake_valid_token(user_email=redactor_email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "redactorEmail": redactor_email,
                "stockId": stock.id,
                "UAICode": "Unknown educational institution",
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"educationalInstitution": "L'établissement n'existe pas"}

    def test_should_not_allow_booking_when_stock_has_no_remaining_quantity(self, app):
        # Given
        stock = offer_factories.EventStockFactory(
            offer__isEducational=True, quantity=0, beginningDatetime=self.stock_date
        )
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=self.educational_year_dates["start"], expirationDate=self.educational_year_dates["end"]
        )
        redactor_email = "professeur.lycee@example.com"

        adage_jwt_fake_valid_token = create_adage_jwt_fake_valid_token(user_email=redactor_email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "redactorEmail": redactor_email,
                "stockId": stock.id,
                "UAICode": educational_institution.institutionId,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"stock": "Il n'y a plus de stock disponible à la réservation sur cette offre"}

    def test_should_not_allow_booking_when_redactor_email_is_different_from_email_in_adage_jwt(self, app):
        # Given
        stock = offer_factories.EventStockFactory(offer__isEducational=True, beginningDatetime=self.stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=self.educational_year_dates["start"], expirationDate=self.educational_year_dates["end"]
        )
        redactor_email = "professeur.lycee@example.com"

        adage_jwt_fake_valid_token = create_adage_jwt_fake_valid_token(user_email="fake@email.com")
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "redactorEmail": redactor_email,
                "stockId": stock.id,
                "UAICode": educational_institution.institutionId,
            },
        )

        # Then
        assert response.status_code == 403
        assert response.json == {"Authorization": "Authenticated email and redactor email do not match"}

    def test_should_not_allow_booking_when_offer_is_not_educational(self, app):
        # Given
        stock = offer_factories.EventStockFactory(offer__isEducational=False, beginningDatetime=self.stock_date)
        redactor_email = "professeur.lycee@example.com"
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=self.educational_year_dates["start"], expirationDate=self.educational_year_dates["end"]
        )

        adage_jwt_fake_valid_token = create_adage_jwt_fake_valid_token(user_email=redactor_email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "redactorEmail": redactor_email,
                "stockId": stock.id,
                "UAICode": educational_institution.institutionId,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"offer": "L'offre n'est pas une offre éducationnelle"}

    def test_should_not_allow_booking_when_offer_is_not_an_event(self, app):
        # Given
        stock = offer_factories.ThingStockFactory(offer__isEducational=True, beginningDatetime=self.stock_date)
        redactor_email = "professeur.lycee@example.com"
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=self.educational_year_dates["start"], expirationDate=self.educational_year_dates["end"]
        )

        adage_jwt_fake_valid_token = create_adage_jwt_fake_valid_token(user_email=redactor_email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "redactorEmail": redactor_email,
                "stockId": stock.id,
                "UAICode": educational_institution.institutionId,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"offer": "L'offre n'est pas un évènement"}
