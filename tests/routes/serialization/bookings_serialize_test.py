from models import EventType, ThingType
from routes.serialization import serialize_booking
from tests.test_utils import create_stock_with_thing_offer, create_venue, \
    create_offerer, create_user, create_booking, create_offer_with_event_product, \
    create_event_occurrence, create_stock_from_event_occurrence, create_user_offerer, \
    create_stock_with_event_offer, create_api_key, create_deposit, create_product_with_thing_type, \
    create_offer_with_thing_product, create_stock
from utils.human_ids import humanize

class SerializeBookingTest:
    def test_should_return_dict_when_offer_is_a_cinema(self, app):
        # Given
        user = create_user(public_name='John Doe', email='user@example.com')
        admin_user = create_user(email='admin@example.com')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer, name='Venue name', address='Venue address')
        offer = create_offer_with_event_product(venue=venue, event_name='Event Name', event_type=EventType.CINEMA)
        event_occurrence = create_event_occurrence(offer, beginning_datetime='2019-11-26 18:29:20.891028')
        stock = create_stock_from_event_occurrence(event_occurrence, price=12)
        booking = create_booking(user, stock=stock, venue=venue, quantity=3)

        # When
        response = serialize_booking(booking)

        # Then
        assert response == {
            'bookingId': humanize(booking.id),
            'dateOfBirth': '',
            'datetime': '2019-11-26 18:29:20.891028',
            'ean13': '',
            'email': 'user@example.com',
            'formula': 'PLACE',
            'isUsed': False,
            'offerId': offer.id,
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

    def test_should_return_dict_when_offer_is_a_subscription_cinema(self, app):
        # Given
        user = create_user(public_name='John Doe', email='user@example.com')
        admin_user = create_user(email='admin@example.com')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer, name='Venue name', address='Venue address')
        product = create_product_with_thing_type(thing_name='Event Name', thing_type=ThingType.CINEMA_ABO, extra_data={'isbn': '123456789'})
        offer = create_offer_with_thing_product(venue, product=product, idx=999)
        stock = create_stock(price=12, offer=offer)
        booking = create_booking(user, stock=stock, venue=venue, quantity=3)

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

    def test_should_return_empty_isbn_when_product_does_not_contain_isbn(self, app):
        # Given
        user = create_user(public_name='John Doe', email='user@example.com')
        admin_user = create_user(email='admin@example.com')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer, name='Venue name', address='Venue address')
        product = create_product_with_thing_type(thing_name='Event Name', thing_type=ThingType.CINEMA_ABO, extra_data={})
        offer = create_offer_with_thing_product(venue, product=product, idx=999)
        stock = create_stock(price=12, offer=offer)
        booking = create_booking(user, stock=stock, venue=venue, quantity=3)

        # When
        response = serialize_booking(booking)

        # Then
        assert response['ean13'] == ''

    def test_should_return_empty_formula_when_offer_is_not_a_cinema(self, app):
        # Given
        user = create_user(public_name='John Doe', email='user@example.com')
        admin_user = create_user(email='admin@example.com')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer, name='Venue name', address='Venue address')
        offer = create_offer_with_event_product(venue=venue, event_name='Event Name', event_type=EventType.JEUX)
        event_occurrence = create_event_occurrence(offer, beginning_datetime='2019-11-26 18:29:20.891028')
        stock = create_stock_from_event_occurrence(event_occurrence, price=12)
        booking = create_booking(user, stock=stock, venue=venue, quantity=3)

        # When
        response = serialize_booking(booking)

        # Then
        assert response['formula'] == ''

    def test_should_return_date_of_birth_and_phone_number_when_offer_is_an_activation(self, app):
        # Given
        user = create_user(public_name='John Doe', email='user@example.com', phone_number='0612345678', date_of_birth='2001-01-01T00:00:00Z')
        admin_user = create_user(email='admin@example.com')
        offerer = create_offerer()
        user_offerer = create_user_offerer(admin_user, offerer)
        venue = create_venue(offerer, name='Venue name', address='Venue address')
        offer = create_offer_with_event_product(venue=venue, event_name='Event Name', event_type=EventType.ACTIVATION)
        event_occurrence = create_event_occurrence(offer, beginning_datetime='2019-11-26 18:29:20.891028')
        stock = create_stock_from_event_occurrence(event_occurrence, price=12)
        booking = create_booking(user, stock=stock, venue=venue, quantity=3)

        # When
        response = serialize_booking(booking)

        # Then
        assert response['dateOfBirth'] == '2001-01-01T00:00:00Z'
        assert response['phoneNumber'] == '0612345678'
