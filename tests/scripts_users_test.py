from datetime import datetime, timedelta

from scripts.users import fill_user_from
from utils.test_utils import create_user


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
