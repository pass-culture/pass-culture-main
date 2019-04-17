import pytest

from datetime import datetime
from tests.conftest import clean_database
from domain.bookings import generate_offer_bookings_details_csv
from models import Booking, PcObject
from tests.test_utils import create_booking, create_deposit, create_stock, create_user, create_offerer, create_venue, \
    create_thing_offer, create_bank_information


@pytest.mark.standalone
class BookingsCSVTest:
    def test_generate_offer_bookings_details_csv_with_headers_and_zero_bookings_lines(self):
        # given
        bookings = []

        # when
        csv = generate_offer_bookings_details_csv(bookings)

        # then
        assert _count_non_empty_lines(csv) == 1

    def test_generate_offer_bookings_details_csv_has_human_readable_header(self):
        # given
        bookings = []

        # when
        csv = generate_offer_bookings_details_csv(bookings)

        # then
        assert _get_header(csv) == '"Date de la réservation","Nom de l\'offre","Nom du lieu","Nom de la structure","Quantité réservée","Prix de la réservation","Réservation annulée","Contremarque validée"\r'

    @clean_database
    def test_generate_offer_bookings_details_csv_with_headers_and_three_bookings_lines(self, app):
        # given
        user = create_user(email='jane.doe@test.com', idx=3)
        offerer = create_offerer(siren='987654321', name='Joe le Libraire')
        venue = create_venue(offerer)
        offer = create_thing_offer(venue)
        stock = create_stock(price=12, available=5, offer=offer)
        booking = create_booking(user, stock, quantity=2)
        deposit1 = create_deposit(user, datetime.utcnow(), amount=100)

        PcObject.check_and_save(user, offerer, venue, offer, stock, booking)

        bookings = Booking.query.all()

        # when
        csv = generate_offer_bookings_details_csv(bookings)
        print('csv', dir(csv), type(csv))

        # then
        assert _count_non_empty_lines(csv) == 2
        assert 'Joe le Libraire' in csv



def _get_header(csv):
    return csv.split('\n')[0]


def _count_non_empty_lines(csv):
    return len(list(filter(lambda line: line != '', csv.split('\n'))))
