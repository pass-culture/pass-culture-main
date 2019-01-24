from datetime import datetime, timedelta

from scripts.users import fill_user_from, create_activation_booking_for
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
        user = fill_user_from(self.csv_row)

        # then
        assert user.lastName == 'Mortimer'
        assert user.firstName == 'Philip'
        assert user.email == 'pmortimer@bletchley.co.uk'
        assert user.phoneNumber == '0123456789'
        assert user.departementCode == '22'
        assert user.postalCode == '22850'

    def test_sets_default_properties_on_the_user(self):
        # when
        user = fill_user_from(self.csv_row)

        # then
        assert user.canBookFreeOffers == False
        assert user.password == ''

    def test_has_a_reset_password_token_and_validity_limit(self):
        # when
        user = fill_user_from(self.csv_row)

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
        user = fill_user_from(self.csv_row, user=existing_user)

        # then
        assert user.id == 123
        assert user.lastName == 'Mortimer'
        assert user.firstName == 'Philip'
        assert user.email == 'pmortimer@bletchley.co.uk'
        assert user.phoneNumber == '0123456789'
        assert user.departementCode == '22'
        assert user.postalCode == '22850'
        assert user.canBookFreeOffers == False
        assert user.password == ''
        assert user.resetPasswordToken is not None
        assert user.resetPasswordTokenValidityLimit is not None


class CreateActivationBookingForTest:
    def test_returns_a_booking_for_given_userr_and_stock(self):
        # given
        venue = create_venue(create_offerer())
        offer = create_thing_offer(venue=venue)
        user = create_user()
        stock = create_stock(offer=offer)

        # when
        booking = create_activation_booking_for(user, stock)

        # then
        assert booking.user == user
        assert booking.stock == stock
        assert booking.quantity == 1
        assert booking.dateCreated.date() == datetime.utcnow().date()

    def test_the_returned_booking_has_a_token_and_is_bookable(self):
        # given
        venue = create_venue(create_offerer())
        offer = create_thing_offer(venue=venue)
        user = create_user()
        stock = create_stock(offer=offer)

        # when
        booking = create_activation_booking_for(user, stock)

        # then
        assert booking.isCancelled == False
        assert booking.isUsed == False
        assert len(booking.token) == 6
