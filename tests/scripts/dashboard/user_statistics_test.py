from models import PcObject
from scripts.dashboard.users_statistics import count_activated_users, count_users_having_booked, \
    get_mean_number_of_bookings_per_user_having_booked, get_mean_amount_spent_by_user
from tests.conftest import clean_database
from tests.test_utils import create_user, create_booking, create_stock, create_offer_with_thing_product, create_venue, \
    create_offerer, create_deposit


class CountActivatedUsersTest:
    @clean_database
    def test_returns_1_when_only_one_active_user(self, app):
        # Given
        user_activated = create_user(can_book_free_offers=True)
        user_not_activated = create_user(can_book_free_offers=False, email='email2@test.com')
        PcObject.save(user_activated, user_not_activated)

        # When
        number_of_active_users = count_activated_users()

        # Then
        assert number_of_active_users == 1


    @clean_database
    def test_returns_0_when_no_active_user(self, app):
        # Given
        user_activated = create_user(can_book_free_offers=False)
        user_not_activated = create_user(can_book_free_offers=False, email='email2@test.com')
        PcObject.save(user_activated, user_not_activated)

        # When
        number_of_active_users = count_activated_users()

        # Then
        assert number_of_active_users == 0


class CountUsersHavingBookedTest:
    @clean_database
    def test_returns_one_when_user_with_one_cancelled_and_one_non_cancelled_bookings(self, app):
        # Given
        user_having_booked = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        offer2 = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer1, price=0)
        stock2 = create_stock(offer=offer2, price=0)
        booking1 = create_booking(user_having_booked, stock1, is_cancelled=False)
        booking2 = create_booking(user_having_booked, stock2, is_cancelled=True)
        PcObject.save(booking1, booking2)

        # When
        number_of_users_having_booked = count_users_having_booked()

        # Then
        assert number_of_users_having_booked == 1


    @clean_database
    def test_returns_two_when_two_users_with_cancelled_bookings(self, app):
        # Given
        user_having_booked1 = create_user()
        user_having_booked2 = create_user(email='test1@email.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking1 = create_booking(user_having_booked1, stock, is_cancelled=True)
        booking2 = create_booking(user_having_booked2, stock, is_cancelled=True)
        PcObject.save(booking1, booking2)

        # When
        number_of_users_having_booked = count_users_having_booked()

        # Then
        assert number_of_users_having_booked == 2


    @clean_database
    def test_returns_zero_when_no_user_with_booking(self, app):
        # Given
        user = create_user()
        PcObject.save(user)

        # When
        number_of_users_having_booked = count_users_having_booked()

        # Then
        assert number_of_users_having_booked == 0


class GetMeanNumberOfBookingsPerUserHavingBookedTest:
    @clean_database
    def test_returns_0_if_no_bookings(self, app):
        # When
        mean_bookings = get_mean_number_of_bookings_per_user_having_booked()

        # Then
        assert mean_bookings == 0


    @clean_database
    def test_returns_1_if_one_user_has_one_non_cancelled_booking(self, app):
        # Given
        user_having_booked = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user_having_booked, stock, is_cancelled=False)
        PcObject.save(booking)
        # When
        mean_bookings = get_mean_number_of_bookings_per_user_having_booked()

        # Then
        assert mean_bookings == 1


    @clean_database
    def test_returns_0_if_one_user_has_one_cancelled_booking(self, app):
        # Given
        user_having_booked = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking = create_booking(user_having_booked, stock, is_cancelled=True)
        PcObject.save(booking)

        # When
        mean_bookings = get_mean_number_of_bookings_per_user_having_booked()

        # Then
        assert mean_bookings == 0


    @clean_database
    def test_returns_0_dot_5_if_one_user_has_one_cancelled_booking_and_another_a_cancelled_one(self, app):
        # Given
        user_having_booked1 = create_user()
        user_having_booked2 = create_user(email='test1@email.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking1 = create_booking(user_having_booked1, stock, is_cancelled=True)
        booking2 = create_booking(user_having_booked2, stock, is_cancelled=False)
        PcObject.save(booking1, booking2)

        # When
        mean_bookings = get_mean_number_of_bookings_per_user_having_booked()

        # Then
        assert mean_bookings == 0.5

class GetMeanAmountSpentByUserTest:
    @clean_database
    def test_returns_0_if_no_bookings(self, app):
        # When
        mean_amount_spent = get_mean_amount_spent_by_user()

        # Then
        assert mean_amount_spent == 0

    @clean_database
    def test_returns_10_if_one_booking_not_cancelled_with_price_10_for_one_user(self, app):
        # Given
        user_having_booked = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)
        booking = create_booking(user_having_booked, stock, is_cancelled=False)
        deposit = create_deposit(user=user_having_booked)
        PcObject.save(booking)

        # When
        mean_amount_spent = get_mean_amount_spent_by_user()

        # Then
        assert mean_amount_spent == 10


    @clean_database
    def test_returns_0_if_one_user_has_one_cancelled_booking(self, app):
        # Given
        user_having_booked = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)
        booking = create_booking(user_having_booked, stock, is_cancelled=True)
        deposit = create_deposit(user=user_having_booked)
        PcObject.save(booking)

        # When
        mean_amount_spent = get_mean_amount_spent_by_user()

        # Then
        assert mean_amount_spent == 0


    @clean_database
    def test_returns_5_if_one_user_has_one_cancelled_booking_and_another_a_cancelled_one_on_stock_price_10(self, app):
        # Given
        user_having_booked1 = create_user()
        user_having_booked2 = create_user(email='test1@email.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)
        booking1 = create_booking(user_having_booked1, stock, is_cancelled=True)
        booking2 = create_booking(user_having_booked2, stock, is_cancelled=False)
        deposit1 = create_deposit(user=user_having_booked1)
        deposit2 = create_deposit(user=user_having_booked2)

        PcObject.save(booking1, booking2)

        # When
        mean_amount_spent = get_mean_amount_spent_by_user()

        # Then
        assert mean_amount_spent == 5