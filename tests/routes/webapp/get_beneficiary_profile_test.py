from datetime import datetime

import pytest

from pcapi.core.bookings.factories import BookingFactory
from pcapi.core.users.factories import UserFactory
from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_with_thing_offer
from pcapi.repository import repository

from tests.conftest import TestClient


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_user_is_logged_in_and_has_no_deposit(self, app):
            # Given
            user = UserFactory(
                email="toto@example.com",
                postalCode="93020",
            )
            repository.delete(*user.deposits)

            # When
            response = TestClient(app.test_client()).with_auth(email="toto@example.com").get("/beneficiaries/current")

            # Then
            assert response.status_code == 200
            json = response.json
            assert json["email"] == "toto@example.com"
            assert json["expenses"] == []
            assert "password" not in json
            assert "clearTextPassword" not in json
            assert "resetPasswordToken" not in json
            assert "resetPasswordTokenValidityLimit" not in json
            assert json["wallet_is_activated"] == False

        @pytest.mark.usefixtures("db_session")
        def when_user_is_logged_in_and_has_a_deposit(self, app):
            # Given
            UserFactory(
                email="wallet_test@email.com",
                postalCode="93020",
                deposit__dateCreated=datetime(2000, 1, 1, 2, 2),
            )

            # When
            response = TestClient(app.test_client()).with_auth("wallet_test@email.com").get("/beneficiaries/current")

            # Then
            assert response.json["wallet_is_activated"] == True
            assert response.json["wallet_date_created"] == "2000-01-01T02:02:00Z"

        @pytest.mark.usefixtures("db_session")
        def when_user_has_booked_some_offers(self, app):
            # Given
            user = UserFactory(
                email="wallet_test@email.com",
                postalCode="93020",
            )

            offerer = create_offerer(
                siren="999199987", address="2 Test adress", city="Test city", postal_code="93000", name="Test offerer"
            )
            venue = create_venue(offerer)
            thing_offer = create_offer_with_thing_product(venue=None)
            stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=5)
            booking = create_booking(user=user, stock=stock, venue=venue, quantity=1)

            repository.save(venue, booking)

            # When
            response = TestClient(app.test_client()).with_auth("wallet_test@email.com").get("/beneficiaries/current")

            # Then
            assert response.json["wallet_balance"] == 495.0
            assert response.json["expenses"] == [
                {"domain": "all", "current": 5.0, "limit": 500.0},
                {"domain": "digital", "current": 0.0, "limit": 200.0},
                {"domain": "physical", "current": 5.0, "limit": 200.0},
            ]

        @pytest.mark.usefixtures("db_session")
        def when_user_has_cancelled_some_offers(self, app):
            # Given
            BookingFactory(isCancelled=True, user__email="wallet_test@email.com", user__postalCode="75130")

            # When
            response = TestClient(app.test_client()).with_auth("wallet_test@email.com").get("/beneficiaries/current")

            # Then
            assert response.json["wallet_balance"] == 500.0
            assert response.json["expenses"] == [
                {"domain": "all", "current": 0.0, "limit": 500.0},
                {"domain": "digital", "current": 0.0, "limit": 200.0},
                {"domain": "physical", "current": 0.0, "limit": 200.0},
            ]

        @pytest.mark.usefixtures("db_session")
        def when_user_is_created_without_postal_code(self, app):
            # Given
            UserFactory(email="wallet_test@email.com", postalCode=None)

            # When
            response = TestClient(app.test_client()).with_auth("wallet_test@email.com").get("/beneficiaries/current")

            # Then
            assert response.status_code == 200

        @pytest.mark.usefixtures("db_session")
        def when_user_is_a_pro(self, app):
            # Given
            user = UserFactory(email="pro@example.com", postalCode=None, isBeneficiary=False, dateOfBirth=None)
            user.suspensionReason = None
            repository.save(user)

            # When
            response = TestClient(app.test_client()).with_auth("pro@example.com").get("/beneficiaries/current")

            # Then
            assert response.status_code == 200
            assert response.json["suspensionReason"] == None

        @pytest.mark.usefixtures("db_session")
        def when_user_is_a_admin(self, app):
            # Given
            UserFactory(email="pro@example.com", postalCode=None, dateOfBirth=None, isAdmin=True)

            # When
            response = TestClient(app.test_client()).with_auth("pro@example.com").get("/beneficiaries/current")

            # Then
            assert response.status_code == 200

        @pytest.mark.usefixtures("db_session")
        def should_return_deposit_version(self, app):
            # Given
            UserFactory(email="wallet_test@email.com", postalCode="93020", deposit__version=1)

            # When
            response = TestClient(app.test_client()).with_auth("wallet_test@email.com").get("/beneficiaries/current")

            # Then

            assert response.json["deposit_version"] == 1

    class Returns401:
        @pytest.mark.usefixtures("db_session")
        def when_user_is_not_logged_in(self, app):
            # When
            response = TestClient(app.test_client()).get("/beneficiaries/current")

            # Then
            assert response.status_code == 401
