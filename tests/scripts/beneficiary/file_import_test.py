from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.models import Booking
from pcapi.models import UserSQLEntity
from pcapi.scripts.beneficiary.file_import import create_booking_for
from pcapi.scripts.beneficiary.file_import import create_users_with_activation_bookings
from pcapi.scripts.beneficiary.file_import import fill_user_from
from pcapi.scripts.beneficiary.file_import import split_rows_in_chunks_with_no_duplicated_emails
from pcapi.utils.token import random_token


class FillUserFromTest:
    def setup_method(self):
        self.csv_row = [
            '68bfabc64b555',
            'Mortimer',
            'Philip',
            'pmortimer@bletchley.co.uk',
            '0123456789',
            'Buckinghamshire (22)',
            '22850',
            '1923-03-15',
            'super_secure_password'
        ]

    @patch('pcapi.scripts.beneficiary.file_import.hash_password')
    def test_returns_an_user_with_data_from_csv_row(self, hashpw):
        # when
        user = fill_user_from(self.csv_row, UserSQLEntity())

        # then
        assert user.lastName == 'Mortimer'
        assert user.firstName == 'Philip'
        assert user.publicName == 'Philip Mortimer'
        assert user.email == 'pmortimer@bletchley.co.uk'
        assert user.phoneNumber == '0123456789'
        assert user.departementCode == '22'
        assert user.postalCode == '22850'
        assert user.dateOfBirth == datetime(1923, 3, 15)
        hashpw.assert_called_with('super_secure_password')

    def test_returns_a_formatted_phone_number(self):
        # given
        data = list(self.csv_row)
        phone_number_with_weird_trailing_chars = '+33 6 59 81 02 26‬‬'
        data[4] = phone_number_with_weird_trailing_chars

        # when
        user = fill_user_from(data, UserSQLEntity())

        # then
        assert user.phoneNumber == '+33659810226'

    def test_returns_only_the_first_firstname(self):
        # given
        data = list(self.csv_row)
        data[2] = 'John Robert James Jack'

        # when
        user = fill_user_from(data, UserSQLEntity())

        # then
        assert user.firstName == 'John'
        assert user.publicName == 'John Mortimer'

    def test_sets_default_properties_on_the_user(self):
        # when
        user = fill_user_from(self.csv_row, UserSQLEntity())

        # then
        assert user.canBookFreeOffers == False
        assert user.password

    def test_has_a_reset_password_token_and_validity_limit(self):
        # when
        user = fill_user_from(self.csv_row, UserSQLEntity())

        # then
        thirty_days_in_the_future = datetime.utcnow() + timedelta(days=30)
        assert user.resetPasswordToken is not None
        assert user.resetPasswordTokenValidityLimit.date() == thirty_days_in_the_future.date()

    def test_returns_the_given_user_with_modified_data_from_the_csv(self):
        # given
        existing_user = create_user(email='pmortimer@bletchley.co.uk', idx=123)

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

    @patch('pcapi.scripts.beneficiary.file_import.random_password')
    def test_returns_an_user_with_computed_password(self, random_password):
        # given
        random_password.return_value = "random_string"
        data = list(self.csv_row)
        del data[8]

        # when
        user = fill_user_from(data, UserSQLEntity())

        # then
        assert user.password == 'random_string'


class CreateBookingForTest:
    def test_returns_a_booking_for_given_user_and_stock(self):
        # given
        venue = create_venue(create_offerer())
        offer = create_offer_with_thing_product(venue=venue)
        user = create_user()
        stock = create_stock(offer=offer)
        token = 'ABC123'

        # when
        booking = create_booking_for(user, stock, token)

        # then
        assert booking.user == user
        assert booking.stock == stock
        assert booking.quantity == 1
        assert booking.amount == 0
        assert booking.dateCreated.date() == datetime.utcnow().date()

    def test_the_returned_booking_has_a_token_and_is_bookable(self):
        # given
        venue = create_venue(create_offerer())
        offer = create_offer_with_thing_product(venue=venue)
        user = create_user()
        stock = create_stock(offer=offer)
        token = 'ABC123'

        # when
        booking = create_booking_for(user, stock, token)

        # then
        assert booking.isCancelled == False
        assert booking.isUsed == False
        assert len(booking.token) == 6


class CreateUsersWithActivationBookingsTest:
    def setup_method(self):
        self.csv_rows = [
            ['68bfa', 'Mortimer', 'Philip', 'pmortimer@bletchley.co.uk', '0123456789', 'Buckinghamshire (22)', '22850',
             '1923-03-15'],
            ['ebf79', 'Blake', 'Francis', 'fblake@bletchley.co.uk', '0987654321', 'Gloucestershire (33)', '33817',
             '1925-06-22'],
            ['ca45d', 'Nasir', 'Ahmed', 'anasir@bletchley.co.uk', '0567891234', 'Worcestershire (44)', '44019',
             '1931-11-02']
        ]
        self.find_user_query = Mock()
        self.find_activation_booking = Mock()

    def test_returns_n_bookings_for_n_csv_rows_on_first_run(self):
        # given
        venue = create_venue(create_offerer())
        offer = create_offer_with_thing_product(venue=venue)
        stock = create_stock(offer=offer)
        self.find_user_query.side_effect = [None, None, None]
        self.find_activation_booking.side_effect = [None, None, None]
        existing_tokens = set()

        # when
        bookings = create_users_with_activation_bookings(
            self.csv_rows, stock, existing_tokens,
            find_user=self.find_user_query,
            find_activation_booking=self.find_activation_booking
        )

        # then
        assert len(bookings) == len(self.csv_rows)

    def test_returns_activation_booking_if_user_already_has_one(self):
        # given
        venue = create_venue(create_offerer())
        offer = create_offer_with_thing_product(venue=venue)
        stock = create_stock(offer=offer)
        self.find_user_query.side_effect = [None, None, None]
        self.find_activation_booking.side_effect = [None, None, Booking()]
        existing_tokens = set()

        # when
        bookings = create_users_with_activation_bookings(
            self.csv_rows, stock, existing_tokens,
            find_user=self.find_user_query,
            find_activation_booking=self.find_activation_booking
        )

        # then
        assert len(bookings) == 3

    def test_finds_users_by_email_before_setting_them_up(self):
        # given
        venue = create_venue(create_offerer())
        offer = create_offer_with_thing_product(venue=venue)
        stock = create_stock(offer=offer)
        blake = create_user(email='fblake@bletchley.co.uk', idx=123)
        self.find_user_query.side_effect = [None, blake, None]
        self.find_activation_booking.side_effect = [None, None, None]
        existing_tokens = set()

        # when
        bookings = create_users_with_activation_bookings(
            self.csv_rows, stock, existing_tokens,
            find_user=self.find_user_query,
            find_activation_booking=self.find_activation_booking
        )

        # then
        assert bookings[1].user.id == 123
        assert bookings[1].user.email == 'fblake@bletchley.co.uk'


class SplitRowsInChunkWithNoDuplicatedEmailsTest:
    def test_returns_a_list_of_list_of_given_chunk_sizes(self):
        # given
        chunk_size = 2
        csv_reader = [
            ['68bfa', 'Mortimer', 'Philip', 'abc@bletchley.co.uk'],
            ['68bfa', 'Mortimer', 'Philip', 'def@bletchley.co.uk'],
            ['68bfa', 'Mortimer', 'Philip', 'ghi@bletchley.co.uk'],
            ['68bfa', 'Mortimer', 'Philip', 'jkl@bletchley.co.uk'],
            ['68bfa', 'Mortimer', 'Philip', 'mno@bletchley.co.uk']
        ]

        # when
        chunked_file = split_rows_in_chunks_with_no_duplicated_emails(csv_reader, chunk_size)

        # then
        assert chunked_file == [
            [
                ['68bfa', 'Mortimer', 'Philip', 'abc@bletchley.co.uk'],
                ['68bfa', 'Mortimer', 'Philip', 'def@bletchley.co.uk']
            ],
            [
                ['68bfa', 'Mortimer', 'Philip', 'ghi@bletchley.co.uk'],
                ['68bfa', 'Mortimer', 'Philip', 'jkl@bletchley.co.uk']
            ],
            [
                ['68bfa', 'Mortimer', 'Philip', 'mno@bletchley.co.uk']
            ]
        ]

    def test_returns_a_list_of_csv_lines_with_no_duplicate_emails(self):
        # given
        chunk_size = 2
        csv_reader = [
            ['68bfa', 'Mortimer', 'Philip', '%s@bletchley.co.uk' % random_token()],
            ['68bfa', 'Mortimer', 'Philip', 'abcd@bletchley.co.uk'],
            ['68bfa', 'Mortimer', 'Philip', '%s@bletchley.co.uk' % random_token()],
            ['68bfa', 'Mortimer', 'Philip', '%s@bletchley.co.uk' % random_token()],
            ['68bfa', 'Mortimer', 'Philip', 'abcd@bletchley.co.uk']
        ]

        # when
        chunked_file = split_rows_in_chunks_with_no_duplicated_emails(csv_reader, chunk_size)

        # then
        assert len(chunked_file) == 2
        assert all(len(chunk) == 2 for chunk in chunked_file[:-1])

    def test_ignores_the_first_line_with_csv_headers(self):
        # given
        chunk_size = 2
        csv_reader = [
            ['id', 'nom', 'prénom', 'email'],
            ['68bfa', 'Mortimer', 'Philip', '%s@bletchley.co.uk' % random_token()],
            ['68bfa', 'Mortimer', 'Philip', '%s@bletchley.co.uk' % random_token()],
            ['68bfa', 'Mortimer', 'Philip', '%s@bletchley.co.uk' % random_token()]
        ]

        # when
        chunked_file = split_rows_in_chunks_with_no_duplicated_emails(csv_reader, chunk_size)

        # then
        assert len(chunked_file) == 2
        assert len(chunked_file[-1]) == 1
        assert all(len(chunk) == 2 for chunk in chunked_file[:-1])

    def test_ignores_empty_lines(self):
        # given
        chunk_size = 2
        csv_reader = [
            ['id', 'nom', 'prénom', 'email'],
            [],
            ['68bfa', 'Mortimer', 'Philip', '%s@bletchley.co.uk' % random_token()],
            [''],
            ['68bfa', 'Mortimer', 'Philip', '%s@bletchley.co.uk' % random_token()]
        ]

        # when
        chunked_file = split_rows_in_chunks_with_no_duplicated_emails(csv_reader, chunk_size)

        # then
        assert len(chunked_file) == 1
        assert len(chunked_file[0]) == 2
