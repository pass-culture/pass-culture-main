from datetime import datetime
from datetime import timedelta
from unittest.mock import patch

import pytest

from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_deposit
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.models import Booking
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


class Put:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def expect_the_booking_to_be_cancelled_by_current_user(self, app):
            # Given
            in_four_days = datetime.utcnow() + timedelta(days=4)
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            stock = create_stock(beginning_datetime=in_four_days, offer=offer)
            booking = create_booking(user=user, stock=stock, venue=venue)
            create_deposit(user, amount=500)
            repository.save(booking)

            # When
            response = (
                TestClient(app.test_client()).with_auth(user.email).put(f"/bookings/{humanize(booking.id)}/cancel")
            )

            # Then
            assert response.status_code == 200
            assert Booking.query.get(booking.id).isCancelled
            assert response.json == {
                "amount": 10.0,
                "completedUrl": None,
                "id": humanize(booking.id),
                "isCancelled": True,
                "quantity": booking.quantity,
                "stock": {"price": 10.0},
                "stockId": humanize(stock.id),
                "token": booking.token,
            }

    class Returns400:
        @pytest.mark.usefixtures("db_session")
        def when_the_booking_cannot_be_cancelled(self, app):
            # Given
            user = create_user()
            booking = create_booking(user=user, is_used=True)
            create_deposit(user, amount=500)
            repository.save(booking)

            # When
            response = (
                TestClient(app.test_client()).with_auth(user.email).put(f"/bookings/{humanize(booking.id)}/cancel")
            )

            # Then
            assert response.status_code == 400
            assert response.json["booking"] == ["Impossible d'annuler une réservation consommée"]
            assert not Booking.query.get(booking.id).isCancelled

    class Returns404:
        @pytest.mark.usefixtures("db_session")
        def when_cancelling_a_booking_of_someone_else(self, app):
            # Given
            other_user = create_user(email="test2@example.com")
            booking = create_booking(other_user)
            user = create_user()
            create_deposit(other_user, amount=500)
            repository.save(user, booking)

            # When
            response = (
                TestClient(app.test_client()).with_auth(user.email).put(f"/bookings/{humanize(booking.id)}/cancel")
            )

            # Then
            assert response.status_code == 404
            assert not Booking.query.get(booking.id).isCancelled

        @pytest.mark.usefixtures("db_session")
        def when_the_booking_does_not_exist(self, app):
            # Given
            user = create_user()
            repository.save(user)

            # When
            response = TestClient(app.test_client()).with_auth(user.email).put("/bookings/AX/cancel")

            # Then
            assert response.status_code == 404
