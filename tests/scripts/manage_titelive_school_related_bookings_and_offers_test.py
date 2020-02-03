import os
from pathlib import Path
from unittest.mock import patch

from models import Offer, Booking
from repository import repository
from scripts.manage_titelive_school_related_bookings_and_offers import _read_token_from_file, \
    manage_titelive_school_related_bookings_and_offers
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_stock, \
    create_booking
from tests.model_creators.specific_creators import create_product_with_thing_type, create_offer_with_thing_product


class ManageTiteliveSchoolRelatedBookingsAndOffersTest:
    @patch('scripts.manage_titelive_school_related_bookings_and_offers._read_token_from_file')
    @clean_database
    def test_should_deactivate_related_offer(self, read_bookings_token_from_file, app):
        # Given
        product = create_product_with_thing_type()
        user = create_user()
        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        offer = create_offer_with_thing_product(venue, product=product, is_active=True)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user=user, stock=stock, token='AZERTY')
        repository.save(venue, product, offer, stock, booking, user)

        read_bookings_token_from_file.return_value = [
            'AZERTY'
        ]

        # When
        manage_titelive_school_related_bookings_and_offers('bookings_file')

        # Then
        offer = Offer.query.one()
        assert not offer.isActive

    @patch('scripts.manage_titelive_school_related_bookings_and_offers._read_token_from_file')
    @clean_database
    def test_should_cancel_booking_if_not_used_yet(self, read_bookings_token_from_file, app):
        # Given
        product = create_product_with_thing_type()
        user = create_user()
        offerer = create_offerer(siren='775671464')
        venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
        offer = create_offer_with_thing_product(venue, product=product, is_active=True)
        stock = create_stock(offer=offer, price=0)
        booking1 = create_booking(user=user, stock=stock, token='AZERTY', is_used=True, is_cancelled=False)
        booking2 = create_booking(user=user, stock=stock, token='AZEDFV', is_cancelled=False)
        repository.save(venue, product, offer, stock, booking1, booking2, user)

        read_bookings_token_from_file.return_value = [
            'AZERTY',
            'AZEDFV'
        ]

        # When
        manage_titelive_school_related_bookings_and_offers('bookings_file')

        # Then
        bookings = Booking.query.all()
        assert not bookings[0].isCancelled
        assert bookings[1].isCancelled

    def test_read_isbn_from_file(self):
        # Given
        file_path = str(Path(os.path.dirname(os.path.realpath(__file__))) \
                        / '..' / '..' / 'sandboxes' / 'scripts' / 'bookings_test_file.txt')

        # When
        bookings_token = _read_token_from_file(file_path)

        # Then
        assert len(bookings_token) == 2
        assert bookings_token[0] == 'Z4FQMU'
        assert bookings_token[1] == '5Y5M2U'
