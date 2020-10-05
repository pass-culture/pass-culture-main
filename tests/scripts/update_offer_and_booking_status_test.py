import os
from pathlib import Path
from unittest.mock import patch

from models import OfferSQLEntity, BookingSQLEntity
from repository import repository
from scripts.update_offer_and_booking_status import _read_booking_tokens_from_file, \
    update_offer_and_booking_status
import pytest
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_stock, \
    create_booking
from tests.model_creators.specific_creators import create_product_with_thing_type, create_offer_with_thing_product


class UpdateOfferAndBookingStatusTest:
    @patch('scripts.update_offer_and_booking_status._read_booking_tokens_from_file')
    @pytest.mark.usefixtures("db_session")
    def test_should_deactivate_related_offer(self, stub_read_bookings_token_from_file, app):
        # Given
        product = create_product_with_thing_type()
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, product=product)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user, stock=stock, token='AZERTY')
        repository.save(venue, product, offer, stock, booking, user)

        stub_read_bookings_token_from_file.return_value = [
            'AZERTY'
        ]

        # When
        update_offer_and_booking_status('fake/path')

        # Then
        offer = OfferSQLEntity.query.one()
        assert not offer.isActive

    @patch('scripts.update_offer_and_booking_status._read_booking_tokens_from_file')
    @pytest.mark.usefixtures("db_session")
    def test_should_cancel_booking_if_not_used_yet(self, stub_read_bookings_token_from_file, app):
        # Given
        product = create_product_with_thing_type()
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue, product=product)
        stock = create_stock(offer=offer, price=0)
        booking1 = create_booking(idx=1, user=user, stock=stock, token='AZERTY', is_used=True, is_cancelled=False)
        booking2 = create_booking(idx=2, user=user, stock=stock, token='AZEDFV', is_cancelled=False)
        repository.save(venue, product, offer, stock, booking1, booking2, user)

        stub_read_bookings_token_from_file.return_value = [
            'AZERTY',
            'AZEDFV'
        ]

        # When
        update_offer_and_booking_status('fake/path')

        # Then
        bookings = BookingSQLEntity.query.order_by(BookingSQLEntity.id.asc()).all()
        assert not bookings[0].isCancelled
        assert bookings[1].isCancelled

    def test_read_booking_tokens_from_file(self):
        # Given
        current_directory = Path(os.path.dirname(os.path.realpath(__file__)))
        file_path = f'{current_directory}/../files/bookings_test_file.txt'

        # When
        bookings_token = _read_booking_tokens_from_file(file_path)

        # Then
        assert len(bookings_token) == 2
        assert bookings_token[0] == 'Z4FQMU'
        assert bookings_token[1] == '5Y5M2U'
