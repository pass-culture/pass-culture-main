from datetime import datetime
from typing import ByteString

from freezegun.api import freeze_time
import pytest

from pcapi.core.bookings.models import Booking
from pcapi.core.educational import factories as educational_factories
from pcapi.core.offers import factories as offer_factories

from tests.conftest import TestClient
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


pytestmark = pytest.mark.usefixtures("db_session")


@freeze_time("2020-11-17 15:00:00")
class PostEducationalBookingTest:
    stock_date = datetime(2021, 5, 15)
    educational_year_dates = {"start": datetime(2020, 9, 1), "end": datetime(2021, 8, 31)}

    def _create_adage_valid_token_with_email(self, email: str) -> ByteString:
        return create_adage_jwt_fake_valid_token(email=email, uai_code="EAU123")

    def test_post_educational_booking(self, app):
        # Given
        stock = offer_factories.EventStockFactory(offer__isEducational=True, beginningDatetime=self.stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_year = educational_factories.EducationalYearFactory(
            beginningDate=self.educational_year_dates["start"], expirationDate=self.educational_year_dates["end"]
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")

        adage_jwt_fake_valid_token = self._create_adage_valid_token_with_email(email=educational_redactor.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "redactorEmail": educational_redactor.email,
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
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")

        adage_jwt_fake_valid_token = self._create_adage_valid_token_with_email(email=educational_redactor.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "redactorEmail": educational_redactor.email,
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
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")

        adage_jwt_fake_valid_token = self._create_adage_valid_token_with_email(email=educational_redactor.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "redactorEmail": educational_redactor.email,
                "stockId": stock.id,
                "UAICode": educational_institution.institutionId,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"stock": "Cette offre n'est pas disponible à la réservation"}

    def test_should_not_allow_booking_when_redactor_email_is_different_from_email_in_adage_jwt(self, app):
        # Given
        stock = offer_factories.EventStockFactory(offer__isEducational=True, beginningDatetime=self.stock_date)
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=self.educational_year_dates["start"], expirationDate=self.educational_year_dates["end"]
        )
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")

        adage_jwt_fake_valid_token = self._create_adage_valid_token_with_email(email="fake@email.com")
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "redactorEmail": educational_redactor.email,
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
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=self.educational_year_dates["start"], expirationDate=self.educational_year_dates["end"]
        )

        adage_jwt_fake_valid_token = self._create_adage_valid_token_with_email(email=educational_redactor.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "redactorEmail": educational_redactor.email,
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
        educational_redactor = educational_factories.EducationalRedactorFactory(email="professeur@example.com")
        educational_institution = educational_factories.EducationalInstitutionFactory()
        educational_factories.EducationalYearFactory(
            beginningDate=self.educational_year_dates["start"], expirationDate=self.educational_year_dates["end"]
        )

        adage_jwt_fake_valid_token = self._create_adage_valid_token_with_email(email=educational_redactor.email)
        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {adage_jwt_fake_valid_token}"}

        # When
        response = test_client.post(
            "/adage-iframe/bookings",
            json={
                "redactorEmail": educational_redactor.email,
                "stockId": stock.id,
                "UAICode": educational_institution.institutionId,
            },
        )

        # Then
        assert response.status_code == 400
        assert response.json == {"offer": "L'offre n'est pas un évènement"}
