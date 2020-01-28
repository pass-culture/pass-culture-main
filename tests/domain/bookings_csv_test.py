from collections import namedtuple
from datetime import datetime

from domain.bookings import generate_bookings_details_csv
from repository import repository
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue, \
    create_deposit
from tests.model_creators.specific_creators import create_offer_with_thing_product
from utils.string_processing import format_decimal


class BookingsCSVTest:
    def test_generate_bookings_details_csv_with_headers_and_zero_bookings_lines(self):
        # given
        bookings = []

        # when
        csv = generate_bookings_details_csv(bookings)

        # then
        assert _count_non_empty_lines(csv) == 1

    def test_generate_bookings_details_csv_has_human_readable_header(self):
        # given
        bookings = []

        # when
        csv = generate_bookings_details_csv(bookings)

        # then
        assert _get_header(
            csv) == 'Raison sociale du lieu;Nom de l\'offre;Nom utilisateur;Prénom utilisateur;E-mail utilisateur;Date de la réservation;Quantité;Tarif pass Culture;Statut'

    @clean_database
    def test_generate_bookings_details_csv_with_headers_and_three_bookings_lines(self, app):
        # given
        user = create_user(email='jane.doe@test.com', idx=3, first_name='John', last_name='Doe')
        offerer = create_offerer(siren='987654321', name='Joe le Libraire')
        venue = create_venue(offerer, name='La petite librairie')
        offer = create_offer_with_thing_product(venue, thing_name='Test Book')
        stock = create_stock(price=12, available=5, offer=offer)
        booking = create_booking(user=user, stock=stock, date_created=datetime(2010, 1, 1, 0, 0, 0, 0))
        deposit = create_deposit(user=user, amount=100)

        repository.save(user, offerer, venue, offer, stock, booking, deposit)

        booking_info = namedtuple(typename='booking_info',
                                  field_names=['venue_name',
                                               'offer_name',
                                               'user_lastname',
                                               'user_firstname',
                                               'user_email',
                                               'date_created',
                                               'quantity',
                                               'amount',
                                               'isCancelled',
                                               'isUsed'])
        booking_info.venue_name = booking.stock.offer.venue.name
        booking_info.offer_name = booking.stock.offer.name
        booking_info.user_lastname = booking.user.lastName
        booking_info.user_firstname = booking.user.firstName
        booking_info.user_email = booking.user.email
        booking_info.date_created = booking.dateCreated
        booking_info.quantity = booking.quantity
        booking_info.amount = format_decimal(booking.amount)
        booking_info.isCancelled = booking.isCancelled
        booking_info.isUsed = booking.isUsed

        expected_line = 'La petite librairie;Test Book;Doe;John;jane.doe@test.com;2010-01-01 00:00:00;1;12;En attente'

        # when
        csv = generate_bookings_details_csv([booking_info])

        # then
        assert _count_non_empty_lines(csv) == 2
        assert csv.split('\r\n')[1] == expected_line


def _get_header(csv):
    return csv.split('\r\n')[0]


def _count_non_empty_lines(csv):
    return len(list(filter(lambda line: line != '', csv.split('\r\n'))))
