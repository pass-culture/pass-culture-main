from datetime import datetime

from freezegun import freeze_time

from domain.booking.booking import Booking
from domain.stock.stock import Stock
from models import EventType, ThingType
from routes.serialization import serialize_booking
from routes.serialization.bookings_serialize import serialize_domain_booking
from tests.domain_creators.generic_creators import create_domain_beneficiary
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue
from tests.model_creators.specific_creators import create_stock_from_event_occurrence, create_product_with_thing_type, \
    create_offer_with_thing_product, create_offer_with_event_product, create_event_occurrence
from utils.human_ids import humanize


class SerializeBookingTest:
    @freeze_time('2019-11-26 18:29:20.891028')
    def test_should_return_dict_when_offer_is_a_cinema(self):
        # Given
        user = create_user(email='user@example.com', public_name='John Doe')
        offerer = create_offerer()
        venue = create_venue(offerer, name='Venue name', address='Venue address')
        offer = create_offer_with_event_product(venue=venue, event_name='Event Name', event_type=EventType.CINEMA)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(event_occurrence, price=12)
        booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)

        # When
        response = serialize_booking(booking)

        # Then
        assert response == {
            'bookingId': humanize(booking.id),
            'dateOfBirth': '',
            'datetime': '2019-11-26T18:29:20.891028Z',
            'ean13': '',
            'email': 'user@example.com',
            'formula': 'PLACE',
            'isUsed': False,
            'offerId': offer.id,
            'publicOfferId': humanize(offer.id),
            'offerName': 'Event Name',
            'offerType': 'EVENEMENT',
            'phoneNumber': '',
            'price': 12,
            'quantity': 3,
            'userName': 'John Doe',
            'venueAddress': 'Venue address',
            'venueDepartementCode': '93',
            'venueName': 'Venue name',
        }

    @freeze_time('2019-11-26 18:29:20.891028')
    def test_should_humanize_ids(self):
        # Given
        user = create_user(email='user@example.com', public_name='John Doe')
        offerer = create_offerer()
        venue = create_venue(offerer, name='Venue name', address='Venue address')
        offer = create_offer_with_event_product(venue=venue, event_name='Event Name', event_type=EventType.CINEMA, idx=999)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(event_occurrence, price=12)
        booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)

        # When
        response = serialize_booking(booking)

        # Then
        assert response['bookingId'] == humanize(booking.id)
        assert response['offerId'] == offer.id
        assert response['publicOfferId'] == humanize(offer.id)

    def test_should_return_dict_when_offer_is_a_subscription_cinema(self):
        # Given
        user = create_user(email='user@example.com', public_name='John Doe')
        offerer = create_offerer()
        venue = create_venue(offerer, name='Venue name', address='Venue address')
        product = create_product_with_thing_type(thing_name='Event Name', thing_type=ThingType.CINEMA_ABO,
                                                 extra_data={'isbn': '123456789'})
        offer = create_offer_with_thing_product(venue, product=product, idx=999)
        stock = create_stock(offer=offer, price=12)
        booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)

        # When
        response = serialize_booking(booking)

        # Then
        assert response == {
            'bookingId': humanize(booking.id),
            'dateOfBirth': '',
            'datetime': '',
            'ean13': '123456789',
            'email': 'user@example.com',
            'formula': 'ABO',
            'isUsed': False,
            'offerId': 999,
            'publicOfferId': 'APTQ',
            'offerName': 'Event Name',
            'offerType': 'BIEN',
            'phoneNumber': '',
            'price': 12,
            'quantity': 3,
            'userName': 'John Doe',
            'venueAddress': 'Venue address',
            'venueDepartementCode': '93',
            'venueName': 'Venue name',
        }

    def test_should_return_empty_isbn_when_product_does_not_contain_isbn(self):
        # Given
        user = create_user(email='user@example.com', public_name='John Doe')
        offerer = create_offerer()
        venue = create_venue(offerer, name='Venue name', address='Venue address')
        product = create_product_with_thing_type(thing_name='Event Name', thing_type=ThingType.CINEMA_ABO,
                                                 extra_data={})
        offer = create_offer_with_thing_product(venue, product=product, idx=999)
        stock = create_stock(offer=offer, price=12)
        booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)

        # When
        response = serialize_booking(booking)

        # Then
        assert response['ean13'] == ''

    @freeze_time('2019-11-26 18:29:20.891028')
    def test_should_return_empty_formula_when_offer_is_not_a_cinema(self):
        # Given
        user = create_user(email='user@example.com', public_name='John Doe')
        offerer = create_offerer()
        venue = create_venue(offerer, name='Venue name', address='Venue address')
        offer = create_offer_with_event_product(venue=venue, event_name='Event Name', event_type=EventType.JEUX)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(event_occurrence, price=12)
        booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)

        # When
        response = serialize_booking(booking)

        # Then
        assert response['formula'] == ''

    @freeze_time('2019-11-26 18:29:20.891028')
    def test_should_return_date_of_birth_and_phone_number_when_offer_is_an_activation(self):
        # Given
        user = create_user(date_of_birth=datetime(2001, 1, 1), email='user@example.com',
                           phone_number='0612345678', public_name='John Doe')
        offerer = create_offerer()
        venue = create_venue(offerer, name='Venue name', address='Venue address')
        offer = create_offer_with_event_product(venue=venue, event_name='Event Name', event_type=EventType.ACTIVATION)
        event_occurrence = create_event_occurrence(offer, beginning_datetime=datetime.utcnow())
        stock = create_stock_from_event_occurrence(event_occurrence, price=12)
        booking = create_booking(user=user, quantity=3, stock=stock, venue=venue)

        # When
        response = serialize_booking(booking)

        # Then
        assert response['dateOfBirth'] == '2001-01-01T00:00:00Z'
        assert response['phoneNumber'] == '0612345678'


class SerializeDomainBookingTest:
    def test_should_return_booking_with_expected_information(self):
        # Give
        offer = create_offer_with_event_product(idx=4)
        user = create_domain_beneficiary(
            identifier=10,
            can_book_free_offers=False,
            email='joe.doe@example.com',
            first_name='Joe',
            last_name='Doe'
        )
        stock = Stock(
            identifier=2,
            quantity=1,
            offer=offer,
            price=10
        )
        booking = Booking(
            identifier=3,
            beneficiary=user,
            stock=stock,
            amount=1,
            quantity=1,
            token='GQTQR9'
        )

        # When
        booking_json = serialize_domain_booking(booking)

        # Then
        assert booking_json == {
            'amount': booking.amount,
            'isCancelled': booking.isCancelled,
            'id': 'AM',
            'stockId': 'A9',
            'quantity': 1,
            'stock': {
                'price': 10
            },
            'token': 'GQTQR9',
            'user': {
                'id': 'B9',
                'wallet_balance': None
            },
            'completedUrl': None
        }
