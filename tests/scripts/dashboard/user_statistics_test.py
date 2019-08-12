from pprint import pprint

import pandas

from models import PcObject
from scripts.dashboard.finance_statistics import get_not_cancelled_bookings_by_departement
from scripts.dashboard.users_statistics import count_activated_users, count_users_having_booked, \
    get_mean_number_of_bookings_per_user_having_booked, get_mean_amount_spent_by_user, \
    _query_get_non_cancelled_bookings_by_user_departement, get_non_cancelled_bookings_by_user_departement
from tests.conftest import clean_database
from tests.test_utils import create_user, create_booking, create_stock, create_offer_with_thing_product, create_venue, \
    create_offerer, create_deposit


class CountActivatedUsersTest:
    @clean_database
    def test_count_all_users_by_default(self, app):
        # Given
        activated_user_from_74 = create_user(can_book_free_offers=True, departement_code='74')
        activated_user_from_75 = create_user(can_book_free_offers=True, departement_code='75', email='email2@test.com')
        PcObject.save(activated_user_from_74, activated_user_from_75)

        # When
        count = count_activated_users()

        # Then
        assert count == 2


    @clean_database
    def test_count_users_by_departement_when_departement_code_given(self, app):
        # Given
        activated_user_from_74 = create_user(can_book_free_offers=True, departement_code='74')
        activated_user_from_75 = create_user(can_book_free_offers=True, departement_code='75', email='email2@test.com')
        PcObject.save(activated_user_from_74, activated_user_from_75)

        # When
        count = count_activated_users('74')

        # Then
        assert count == 1


class CountUsersHavingBookedTest:
    @clean_database
    def test_count_all_users_by_default(self, app):
        # Given
        activated_user_from_74 = create_user(can_book_free_offers=True, departement_code='74')
        activated_user_from_75 = create_user(can_book_free_offers=True, departement_code='75', email='email2@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer1, price=0)
        booking1 = create_booking(activated_user_from_74, stock1)
        booking2 = create_booking(activated_user_from_75, stock1)
        PcObject.save(booking1, booking2)
        PcObject.save(activated_user_from_74, activated_user_from_75)

        # When
        count = count_users_having_booked()

        # Then
        assert count == 2


    @clean_database
    def test_count_users_by_departement_when_departement_code_given(self, app):
        # Given
        activated_user_from_74 = create_user(can_book_free_offers=True, departement_code='74')
        activated_user_from_75 = create_user(can_book_free_offers=True, departement_code='75', email='email2@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer1, price=0)
        booking1 = create_booking(activated_user_from_74, stock1)
        booking2 = create_booking(activated_user_from_75, stock1)
        PcObject.save(booking1, booking2)
        PcObject.save(activated_user_from_74, activated_user_from_75)

        # When
        count = count_users_having_booked('74')

        # Then
        assert count == 1


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
    def test_returns_20_if_one_booking_with_price_10_with_2_as_quantity(self, app):
        # Given
        user_having_booked = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)
        booking = create_booking(user_having_booked, stock, is_cancelled=False, quantity=2)
        deposit = create_deposit(user=user_having_booked)
        PcObject.save(booking)

        # When
        mean_amount_spent = get_mean_amount_spent_by_user()

        # Then
        assert mean_amount_spent == 20

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


class GetNotCancelledBookingsByDepartementTest:
    @clean_database
    def test_return_number_of_booking_by_departement(self, app):
        # Given
        _create_departement_booking_for_users(departement_code='08', user_email='test1@email.com', booking_count=2, siren='111111111')
        _create_departement_booking_for_users(departement_code='34', user_email='test2@email.com', booking_count=10, siren='222222222')


        expected_counts = [('08', 2), ('34', 10)]
        expected_table = pandas.DataFrame(columns=['Departement', 'Nombre de réservations'],
                                          data=expected_counts)

        # When
        bookings_counts = get_not_cancelled_bookings_by_departement()

        # Then
        assert bookings_counts.eq(expected_table).all().all()


class QueryGetNonCancelledBookingsByDepartementTest:
    @clean_database
    def test_should_ignore_cancelled_bookings(self, app):
        # Given
        offerer = create_offerer(name='Offerer dans le 93')
        venue = create_venue(offerer, departement_code='93')
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)

        user_in_93 = create_user(departement_code='93')
        create_deposit(user_in_93, amount=500)
        booking = create_booking(user_in_93, stock, quantity=1, is_cancelled=True)
        PcObject.save(booking)

        # When
        bookings_by_departement = _query_get_non_cancelled_bookings_by_user_departement()

        # Then
        assert len(bookings_by_departement) == 0

    @clean_database
    def test_should_return_all_bookings_by_departement(self, app):
        # Given
        offerer = create_offerer(name='Offerer dans le 93')
        venue = create_venue(offerer, departement_code='93')
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)

        user_in_93 = create_user(departement_code='93')
        create_deposit(user_in_93, amount=500)
        booking = create_booking(user_in_93, stock, quantity=1)
        booking2 = create_booking(user_in_93, stock, quantity=1)
        PcObject.save(booking, booking2)

        # When
        bookings_by_departement = _query_get_non_cancelled_bookings_by_user_departement()

        # Then
        assert len(bookings_by_departement) == 1
        assert bookings_by_departement == [('93', 2)]

    @clean_database
    def test_should_return_count_booking_based_on_user_location_not_venue_location(self, app):
        # Given
        offerer = create_offerer(name='Offerer dans le 93 et dans le 95', siren=111111111)
        venue93 = create_venue(offerer, departement_code='93', siret=11111111100001)
        offer93 = create_offer_with_thing_product(venue93)
        stock93 = create_stock(offer=offer93, price=10)

        venue95 = create_venue(offerer, departement_code='95', siret=11111111100002)
        offer95 = create_offer_with_thing_product(venue95)
        stock95 = create_stock(offer=offer95, price=10)

        user_in_93 = create_user(departement_code='76')
        create_deposit(user_in_93, amount=500)
        booking = create_booking(user_in_93, stock93, quantity=5)
        booking2 = create_booking(user_in_93, stock95, quantity=2)
        PcObject.save(booking, booking2)

        # When
        bookings_by_departement = _query_get_non_cancelled_bookings_by_user_departement()

        # Then
        assert len(bookings_by_departement) == 1
        assert bookings_by_departement == [('76', 7)]


    @clean_database
    def test_should_return_multiple_departements_and_order_by_departementCode(self, app):
        # Given
        offerer93 = create_offerer(name='Offerer dans le 93', siren=111111111)
        venue93 = create_venue(offerer93, departement_code='93', siret=11111111100001)
        offer93 = create_offer_with_thing_product(venue93)
        stock93 = create_stock(offer=offer93, price=10)

        offerer95 = create_offerer(name='Offerer dans le 95', siren=222222222)
        venue95 = create_venue(offerer95, departement_code='95', siret=22222222200001)
        offer95 = create_offer_with_thing_product(venue95)
        stock95 = create_stock(offer=offer95, price=10)

        user_in_95 = create_user(departement_code='95', email="user_in_95@example.net")
        create_deposit(user_in_95, amount=500)
        booking_in_95 = create_booking(user_in_95, stock95, quantity=5)

        user_in_93 = create_user(departement_code='93', email="user_in_93@example.net")
        create_deposit(user_in_93, amount=500)
        booking_in_93 = create_booking(user_in_93, stock93, quantity=2)

        PcObject.save(booking_in_93, booking_in_95)

        # When
        bookings_by_departement = _query_get_non_cancelled_bookings_by_user_departement()

        # Then
        assert len(bookings_by_departement) == 2
        assert bookings_by_departement == [('93', 2), ('95', 5)]


class GetNonCancelledBookingsFilteredByUserDepartementTest:
    @clean_database
    def test_returns_bookings_filtered_by_user_departement(self, app):
        # Given
        bookings = [('93', 2), ('95', 1), ('973', 15)]
        bookings_to_save = _create_bookings_for_departement(bookings)
        PcObject.save(*bookings_to_save)
        expected_counts = [
            ('93', 2), ('95', 1), ('973', 15)
        ]
        expected_table = pandas.DataFrame(columns=['Département de l\'utilisateur', 'Nombre de réservations'],
                                          data=expected_counts)

        # When
        bookings_by_departement = get_non_cancelled_bookings_by_user_departement()

        # Then
        pprint(bookings_by_departement)
        assert bookings_by_departement.eq(expected_table).all().all()


def _create_departement_booking_for_users(departement_code, user_email, booking_count, siren):
    user_having_booked = create_user(departement_code=departement_code, email=user_email)

    offerer = create_offerer(siren=siren)
    venue = create_venue(offerer, siret=siren + '12345')
    offer = create_offer_with_thing_product(venue)
    stock = create_stock(offer=offer, price=0)

    for i in range(booking_count):
        create_booking(user_having_booked, stock, is_cancelled=False)

    PcObject.save(stock)


def _create_bookings_for_departement(bookings_by_departement):
    bookings = []

    offerer = create_offerer(name='Offerer', siren=222222222)
    venue = create_venue(offerer, departement_code='95', siret=22222222200001)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock(offer=offer, price=10, available=1000)

    for departement_code, quantity in bookings_by_departement:
        user = create_user(departement_code=departement_code, email=f"user_in_{departement_code}@example.net")
        create_deposit(user, amount=500)
        bookings.append(create_booking(user, stock, quantity=quantity))

    return bookings
