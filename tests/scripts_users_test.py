from datetime import datetime, timedelta
from unittest.mock import Mock

from models import User
from scripts.users import fill_user_from, create_activation_booking_for, setup_users
from utils.test_utils import create_user, create_stock, create_thing_offer, create_venue, create_offerer


class FillUserFromTest:
    def setup_method(self):
        self.csv_row = [
            '68bfabc64b555',
            'Mortimer',
            'Philip',
            'pmortimer@bletchley.co.uk',
            '0123456789',
            'Buckinghamshire (22)',
            '22850'
        ]

    def test_returns_an_user_with_data_from_csv_row(self):
        # when
        user = fill_user_from(self.csv_row, User())

        # then
        assert user.lastName == 'Mortimer'
        assert user.firstName == 'Philip'
        assert user.publicName == 'Philip M.'
        assert user.email == 'pmortimer@bletchley.co.uk'
        assert user.phoneNumber == '0123456789'
        assert user.departementCode == '22'
        assert user.postalCode == '22850'

    def test_returns_a_formatted_phone_number(self):
        # given
        data = list(self.csv_row)
        phone_number_with_weird_trailing_chars = '+33 6 59 81 02 26‬‬'
        data[4] = phone_number_with_weird_trailing_chars

        # when
        user = fill_user_from(data, User())

        # then
        assert user.phoneNumber == '+33659810226'

    def test_returns_only_the_first_firstname(self):
        # given
        data = list(self.csv_row)
        data[2] = 'John Robert James Jack'

        # when
        user = fill_user_from(data, User())

        # then
        assert user.firstName == 'John'
        assert user.publicName == 'John M.'

    def test_sets_default_properties_on_the_user(self):
        # when
        user = fill_user_from(self.csv_row, User())

        # then
        assert user.canBookFreeOffers == False
        assert user.password != ''

    def test_has_a_reset_password_token_and_validity_limit(self):
        # when
        user = fill_user_from(self.csv_row, User())

        # then
        thirty_days_in_the_future = datetime.utcnow() + timedelta(days=30)
        assert user.resetPasswordToken is not None
        assert user.resetPasswordTokenValidityLimit.date() == thirty_days_in_the_future.date()

    def test_returns_the_given_user_with_modified_data_from_the_csv(self):
        # given
        existing_user = create_user(
            idx=123,
            email='pmortimer@bletchley.co.uk'
        )

        # when
        user = fill_user_from(self.csv_row, existing_user)

        # then
        assert user.id == 123
        assert user.lastName == 'Mortimer'
        assert user.firstName == 'Philip'
        assert user.email == 'pmortimer@bletchley.co.uk'
        assert user.phoneNumber == '0123456789'
        assert user.departementCode == '22'
        assert user.postalCode == '22850'
        assert user.canBookFreeOffers == False
        assert user.password != ''
        assert user.resetPasswordToken is not None
        assert user.resetPasswordTokenValidityLimit is not None


class CreateActivationBookingForTest:
    def test_returns_a_booking_for_given_userr_and_stock(self):
        # given
        venue = create_venue(create_offerer())
        offer = create_thing_offer(venue=venue)
        user = create_user()
        stock = create_stock(offer=offer)
        token = 'ABC123'

        # when
        booking = create_activation_booking_for(user, stock, token)

        # then
        assert booking.user == user
        assert booking.stock == stock
        assert booking.quantity == 1
        assert booking.amount == 0
        assert booking.dateCreated.date() == datetime.utcnow().date()

    def test_the_returned_booking_has_a_token_and_is_bookable(self):
        # given
        venue = create_venue(create_offerer())
        offer = create_thing_offer(venue=venue)
        user = create_user()
        stock = create_stock(offer=offer)
        token = 'ABC123'

        # when
        booking = create_activation_booking_for(user, stock, token)

        # then
        assert booking.isCancelled == False
        assert booking.isUsed == False
        assert len(booking.token) == 6


class SetupUsersTest:
    def setup_method(self):
        self.csv_rows = [
            ['68bfa', 'Mortimer', 'Philip', 'pmortimer@bletchley.co.uk', '0123456789', 'Buckinghamshire (22)', '22850'],
            ['ebf79', 'Blake', 'Francis', 'fblake@bletchley.co.uk', '0987654321', 'Gloucestershire (33)', '33817'],
            ['ca45d', 'Nasir', 'Ahmed', 'anasir@bletchley.co.uk', '0567891234', 'Worcestershire (44)', '44019']
        ]
        self.mocked_query = Mock()

    def test_returns_n_bookings_for_n_csv_rows(self):
        # given
        venue = create_venue(create_offerer())
        offer = create_thing_offer(venue=venue)
        stock = create_stock(offer=offer)
        self.mocked_query.side_effect = [None, None, None]
        existing_tokens = set()

        # when
        bookings = setup_users(self.csv_rows, stock, existing_tokens, find_user_query=self.mocked_query)

        # then
        assert len(bookings) == len(self.csv_rows)

    def test_finds_users_by_email_before_setting_them_up(self):
        # given
        venue = create_venue(create_offerer())
        offer = create_thing_offer(venue=venue)
        stock = create_stock(offer=offer)
        blake = create_user(idx=123, email='fblake@bletchley.co.uk')
        self.mocked_query.side_effect = [None, blake, None]
        existing_tokens = set()

        # when
        bookings = setup_users(self.csv_rows, stock, existing_tokens, find_user_query=self.mocked_query)

        # then
        assert bookings[1].user.id == 123
        assert bookings[1].user.email == 'fblake@bletchley.co.uk'
