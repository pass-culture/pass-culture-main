from datetime import datetime

import pytest

from pcapi.core.bookings import factories
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
                email="toto@btmx.fr",
                postalCode="93020",
            )
            repository.delete(*user.deposits)

            # When
            response = TestClient(app.test_client()).with_auth(email="toto@btmx.fr").get("/beneficiaries/current")

            # Then
            assert response.status_code == 200
            json = response.json
            assert json["email"] == "toto@btmx.fr"
            assert json["expenses"] == []
            assert "password" not in json
            assert "clearTextPassword" not in json
            assert "resetPasswordToken" not in json
            assert "resetPasswordTokenValidityLimit" not in json
            assert json["wallet_is_activated"] == False

        @pytest.mark.usefixtures("db_session")
        def when_user_is_logged_in_and_has_a_deposit(self, app):
            # Given
            user = UserFactory(
                email="wallet_test@email.com",
                postalCode="93020",
            )

            deposit = user.deposits[0]
            deposit.dateCreated = datetime(2000, 1, 1, 2, 2)
            repository.save(deposit)

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
                {"domain": "all", "current": 5.0, "max": 500.0},
                {"domain": "digital", "current": 0.0, "max": 200.0},
                {"domain": "physical", "current": 5.0, "max": 200.0},
            ]

        @pytest.mark.usefixtures("db_session")
        def when_user_has_cancelled_some_offers(self, app):
            # Given
            booking = factories.BookingFactory(
                isCancelled=True, user__email="wallet_test@email.com", user__postalCode="75130"
            )
            repository.save(booking)

            # When
            response = TestClient(app.test_client()).with_auth("wallet_test@email.com").get("/beneficiaries/current")

            # Then
            assert response.json["wallet_balance"] == 500.0
            assert response.json["expenses"] == [
                {"domain": "all", "current": 0.0, "max": 500.0},
                {"domain": "digital", "current": 0.0, "max": 200.0},
                {"domain": "physical", "current": 0.0, "max": 200.0},
            ]

    class Returns401:
        @pytest.mark.usefixtures("db_session")
        def when_user_is_not_logged_in(self, app):
            # When
            response = TestClient(app.test_client()).get("/beneficiaries/current")

            # Then
            assert response.status_code == 401
