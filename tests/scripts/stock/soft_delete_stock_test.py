from unittest.mock import patch

import pytest

from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_payment
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.repository import repository
from pcapi.scripts.stock.soft_delete_stock import soft_delete_stock


class SoftDeleteStockTest:
    @patch("pcapi.scripts.stock.soft_delete_stock.repository")
    @pytest.mark.usefixtures("db_session")
    def should_return_ko_if_at_least_one_booking_is_used(self, mock_repository, app):
        # Given
        user = create_user()
        stock = create_stock(price=0)
        booking = create_booking(is_used=True, stock=stock, user=user)

        repository.save(booking)

        # When
        soft_delete_stock(stock.id)

        # Then
        assert mock_repository.save.call_count == 0

    @patch("pcapi.scripts.stock.soft_delete_stock.repository")
    @pytest.mark.usefixtures("db_session")
    def should_return_ko_if_at_least_one_booking_has_payments(self, mock_repository, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        stock = create_stock(price=0)
        booking = create_booking(stock=stock, user=user)
        payment = create_payment(booking=booking, offerer=offerer)

        repository.save(booking, payment)

        # When
        soft_delete_stock(stock.id)

        # Then
        assert mock_repository.save.call_count == 0

    @patch("pcapi.scripts.stock.soft_delete_stock.repository")
    @pytest.mark.usefixtures("db_session")
    def should_return_ok_if_stock_has_no_bookings(self, mock_repository, app):
        # Given
        offerer = create_offerer()
        user = create_user()
        stock = create_stock(price=0)
        booking = create_booking(stock=stock, user=user)
        payment = create_payment(booking=booking, offerer=offerer)

        repository.save(booking, payment)

        # When
        soft_delete_stock(stock.id)

        # Then
        assert mock_repository.save.call_count == 0

    @patch("pcapi.scripts.stock.soft_delete_stock.repository")
    @patch("pcapi.core.bookings.api.repository")
    @pytest.mark.usefixtures("db_session")
    def should_cancel_every_bookings_for_target_stock(self, mock_repository, mock_repository_1, app):
        # Given
        user = create_user()
        stock = create_stock(price=0)
        booking = create_booking(stock=stock, user=user)

        repository.save(booking)

        # When
        soft_delete_stock(stock.id)

        # Then
        assert mock_repository.save.call_count == 1
        assert mock_repository_1.save.call_count == 1
        assert booking.isCancelled == True

    @patch("pcapi.scripts.stock.soft_delete_stock.repository")
    @patch("pcapi.core.bookings.api.repository")
    @pytest.mark.usefixtures("db_session")
    def should_soft_delete_target_stock(self, mock_repository, mock_repository_1, app):
        # Given
        user = create_user()
        stock = create_stock(price=0)
        booking = create_booking(stock=stock, user=user)

        repository.save(booking)

        # When
        soft_delete_stock(stock.id)

        # Then
        assert mock_repository.save.call_count == 1
        assert mock_repository_1.save.call_count == 1
        assert stock.isSoftDeleted == True
