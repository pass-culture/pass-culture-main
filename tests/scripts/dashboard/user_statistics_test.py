import pandas

from models import ThingType, EventType
from repository import repository
from scripts.dashboard.users_statistics import count_activated_users, count_users_having_booked, \
    get_mean_number_of_bookings_per_user_having_booked, get_mean_amount_spent_by_user, \
    _query_get_non_cancelled_bookings_by_user_departement, get_non_cancelled_bookings_by_user_departement
from tests.conftest import clean_database
from tests.model_creators.generic_creators import create_booking, create_user, create_stock, create_offerer, \
    create_venue, \
    create_deposit
from tests.model_creators.specific_creators import create_offer_with_thing_product, create_offer_with_event_product


class CountActivatedUsersTest:
    @clean_database
    def test_count_all_users_by_default(self, app):
        # Given
        activated_user_from_74 = create_user(can_book_free_offers=True, departement_code='74')
        activated_user_from_75 = create_user(can_book_free_offers=True, departement_code='75',
                                             email='email2@test.com')
        repository.save(activated_user_from_74, activated_user_from_75)

        # When
        count = count_activated_users()

        # Then
        assert count == 2

    @clean_database
    def test_count_users_by_departement_when_departement_code_given(self, app):
        # Given
        activated_user_from_74 = create_user(can_book_free_offers=True, departement_code='74')
        activated_user_from_75 = create_user(can_book_free_offers=True, departement_code='75',
                                             email='email2@test.com')
        repository.save(activated_user_from_74, activated_user_from_75)

        # When
        count = count_activated_users('74')

        # Then
        assert count == 1


class CountUsersHavingBookedTest:
    @clean_database
    def test_count_all_users_by_default(self, app):
        # Given
        activated_user_from_74 = create_user(can_book_free_offers=True, departement_code='74')
        activated_user_from_75 = create_user(can_book_free_offers=True, departement_code='75',
                                             email='email2@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer1, price=0)
        booking1 = create_booking(activated_user_from_74, stock=stock1)
        booking2 = create_booking(activated_user_from_75, stock=stock1)
        repository.save(booking1, booking2)
        repository.save(activated_user_from_74, activated_user_from_75)

        # When
        count = count_users_having_booked()

        # Then
        assert count == 2

    @clean_database
    def test_does_not_count_users_having_booked_activation_offer(self, app):
        # Given
        user1 = create_user(can_book_free_offers=True, departement_code='74')
        user2 = create_user(can_book_free_offers=True, departement_code='75', email='email2@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=0)
        stock2 = create_stock(offer=offer2, price=0)
        booking1 = create_booking(user=user1, stock=stock1)
        booking2 = create_booking(user=user2, stock=stock2)
        repository.save(booking1, booking2)

        # When
        count = count_users_having_booked()

        # Then
        assert count == 0

    @clean_database
    def test_count_users_by_departement_when_departement_code_given(self, app):
        # Given
        activated_user_from_74 = create_user(can_book_free_offers=True, departement_code='74')
        activated_user_from_75 = create_user(can_book_free_offers=True, departement_code='75',
                                             email='email2@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue)
        stock1 = create_stock(offer=offer1, price=0)
        booking1 = create_booking(activated_user_from_74, stock=stock1)
        booking2 = create_booking(activated_user_from_75, stock=stock1)
        repository.save(booking1, booking2)
        repository.save(activated_user_from_74, activated_user_from_75)

        # When
        count = count_users_having_booked('74')

        # Then
        assert count == 1

    @clean_database
    def test_does_not_count_users_having_booked_activation_offer_when_departement_code_given(self, app):
        # Given
        user1 = create_user(can_book_free_offers=True, departement_code='74')
        user2 = create_user(can_book_free_offers=True, departement_code='74', email='email2@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=0)
        stock2 = create_stock(offer=offer2, price=0)
        booking1 = create_booking(user=user1, stock=stock1)
        booking2 = create_booking(user=user2, stock=stock2)
        repository.save(booking1, booking2)

        # When
        count = count_users_having_booked('74')

        # Then
        assert count == 0


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
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=False)
        repository.save(booking)

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
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=True)
        repository.save(booking)

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
        booking1 = create_booking(user=user_having_booked1, stock=stock, is_cancelled=True)
        booking2 = create_booking(user=user_having_booked2, stock=stock, is_cancelled=False)
        repository.save(booking1, booking2)

        # When
        mean_bookings = get_mean_number_of_bookings_per_user_having_booked()

        # Then
        assert mean_bookings == 0.5

    @clean_database
    def test_returns_one_if_only_one_user_is_from_the_good_departement(self, app):
        # Given
        user_having_booked1 = create_user(departement_code='45')
        user_having_booked2 = create_user(departement_code='91', email='test1@email.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=0)
        booking1 = create_booking(user=user_having_booked1, stock=stock, is_cancelled=False)
        booking2 = create_booking(user=user_having_booked2, stock=stock, is_cancelled=False)
        repository.save(booking1, booking2)

        # When
        mean_bookings = get_mean_number_of_bookings_per_user_having_booked('45')

        # Then
        assert mean_bookings == 1.0

    @clean_database
    def test_returns_zero_if_users_have_only_activation_bookings(self, app):
        # Given
        user1 = create_user()
        user2 = create_user(email='e@mail.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=0)
        stock2 = create_stock(offer=offer2, price=0)
        booking1 = create_booking(user=user1, stock=stock1, is_cancelled=False)
        booking2 = create_booking(user=user2, stock=stock2, is_cancelled=False)
        repository.save(booking1, booking2)

        # When
        mean_bookings = get_mean_number_of_bookings_per_user_having_booked()

        # Then
        assert mean_bookings == 0.0

    @clean_database
    def test_returns_one_if_one_user_has_only_activation_booking_and_one_user_has_one_cinema_booking(self, app):
        # Given
        user1 = create_user()
        user2 = create_user(email='e@mail.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_event_product(venue, event_type=EventType.CINEMA)
        stock1 = create_stock(offer=offer1, price=0)
        stock2 = create_stock(offer=offer2, price=0)
        booking1 = create_booking(user=user1, stock=stock1, is_cancelled=False)
        booking2 = create_booking(user=user2, stock=stock2, is_cancelled=False)
        repository.save(booking1, booking2)

        # When
        mean_bookings = get_mean_number_of_bookings_per_user_having_booked()

        # Then
        assert mean_bookings == 1.0


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
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=False)
        deposit = create_deposit(user=user_having_booked)
        repository.save(booking)

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
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=False, quantity=2)
        deposit = create_deposit(user=user_having_booked)
        repository.save(booking)

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
        booking = create_booking(user=user_having_booked, stock=stock, is_cancelled=True)
        deposit = create_deposit(user=user_having_booked)
        repository.save(booking)

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
        booking1 = create_booking(user=user_having_booked1, stock=stock, is_cancelled=True)
        booking2 = create_booking(user=user_having_booked2, stock=stock, is_cancelled=False)
        deposit1 = create_deposit(user=user_having_booked1)
        deposit2 = create_deposit(user=user_having_booked2)

        repository.save(booking1, booking2)

        # When
        mean_amount_spent = get_mean_amount_spent_by_user()

        # Then
        assert mean_amount_spent == 5

    @clean_database
    def test_returns_30_if_one_user_has_only_one_non_activation_booking_with_price_30(self, app):
        # Given
        user = create_user()
        offerer = create_offerer()
        venue = create_venue(offerer)
        activation_offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        activation_offer2 = create_offer_with_event_product(venue, event_type=EventType.ACTIVATION)
        offer = create_offer_with_thing_product(venue, thing_type=ThingType.CINEMA_ABO)
        activation_stock1 = create_stock(offer=activation_offer1, price=6)
        activation_stock2 = create_stock(offer=activation_offer2, price=10)
        stock = create_stock(offer=offer, price=30)
        activation_booking1 = create_booking(user=user, stock=activation_stock1)
        activation_booking2 = create_booking(user=user, stock=activation_stock2)
        booking = create_booking(user=user, stock=stock)
        deposit = create_deposit(user=user)

        repository.save(activation_booking1, activation_booking2, booking)

        # When
        mean_amount_spent = get_mean_amount_spent_by_user()

        # Then
        assert mean_amount_spent == 30.0

    @clean_database
    def test_returns_average_amount_based_on_user_location(self, app):
        # Given
        user_having_booked_from_25 = create_user(departement_code='25', email='email75@example.net')
        user_having_booked_from_63 = create_user(departement_code='63', email='email63@example.net')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock = create_stock(offer=offer, price=10)
        expensive_stock = create_stock(offer=offer, price=200)
        booking_for_user_one = create_booking(user=user_having_booked_from_25, stock=stock, is_cancelled=False)
        booking_for_user_two = create_booking(user=user_having_booked_from_63, stock=expensive_stock, is_cancelled=False)
        firstDeposit = create_deposit(user=user_having_booked_from_25)
        secondDeposit = create_deposit(user=user_having_booked_from_63)
        repository.save(booking_for_user_one, booking_for_user_two)

        # When
        mean_amount_spent = get_mean_amount_spent_by_user('25')

        # Then
        assert mean_amount_spent == 10


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
        booking = create_booking(user=user_in_93, stock=stock, is_cancelled=True, quantity=1)
        repository.save(booking)

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
        booking = create_booking(user=user_in_93, stock=stock, quantity=1)
        booking2 = create_booking(user=user_in_93, stock=stock, quantity=1)
        repository.save(booking, booking2)

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
        booking = create_booking(user=user_in_93, stock=stock93, quantity=5)
        booking2 = create_booking(user=user_in_93, stock=stock95, quantity=2)
        repository.save(booking, booking2)

        # When
        bookings_by_departement = _query_get_non_cancelled_bookings_by_user_departement()

        # Then
        assert len(bookings_by_departement) == 1
        assert bookings_by_departement == [('76', 7)]

    @clean_database
    def test_should_return_multiple_departements_and_order_by_desc_booking_counts(self, app):
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
        booking_in_95 = create_booking(user=user_in_95, stock=stock95, quantity=5)

        user_in_93 = create_user(departement_code='93', email="user_in_93@example.net")
        create_deposit(user_in_93, amount=500)
        booking_in_93 = create_booking(user=user_in_93, stock=stock93, quantity=2)

        repository.save(booking_in_93, booking_in_95)

        # When
        bookings_by_departement = _query_get_non_cancelled_bookings_by_user_departement()

        # Then
        assert len(bookings_by_departement) == 2
        assert bookings_by_departement == [('95', 5), ('93', 2)]

    @clean_database
    def test_should_return_zero_bookings_if_they_are_on_activation_offers(self, app):
        # Given
        offerer = create_offerer(name='Offerer dans le 93')
        venue = create_venue(offerer, departement_code='93')
        offer1 = create_offer_with_thing_product(venue, thing_type=ThingType.ACTIVATION)
        offer2 = create_offer_with_thing_product(venue, thing_type=EventType.ACTIVATION)
        stock1 = create_stock(offer=offer1, price=10)
        stock2 = create_stock(offer=offer2, price=10)

        user_in_93 = create_user(departement_code='93')
        create_deposit(user_in_93, amount=500)
        booking1 = create_booking(user=user_in_93, stock=stock1, quantity=1)
        booking2 = create_booking(user=user_in_93, stock=stock2, quantity=1)
        repository.save(booking1, booking2)

        # When
        bookings_by_departement = _query_get_non_cancelled_bookings_by_user_departement()

        # Then
        print(bookings_by_departement)
        assert len(bookings_by_departement) == 0


class GetNonCancelledBookingsFilteredByUserDepartementTest:
    @clean_database
    def test_returns_bookings_filtered_by_user_departement_and_ordered_by_descending_order_on_number_of_bookings(self,
                                                                                                                 app):
        # Given
        bookings = [('93', 2), ('95', 1), ('973', 15)]
        bookings_to_save = _create_bookings_for_departement(bookings)
        repository.save(*bookings_to_save)
        expected_counts = [
            ('973', 15), ('93', 2), ('95', 1)
        ]
        expected_table = pandas.DataFrame(columns=['Département de l\'utilisateur', 'Nombre de réservations'],
                                          data=expected_counts)

        # When
        bookings_by_departement = get_non_cancelled_bookings_by_user_departement()

        # Then
        assert bookings_by_departement.eq(expected_table).all().all()


def _create_departement_booking_for_users(departement_code, user_email, booking_count, siren):
    user_having_booked = create_user(departement_code=departement_code, email=user_email)

    offerer = create_offerer(siren=siren)
    venue = create_venue(offerer, siret=siren + '12345')
    offer = create_offer_with_thing_product(venue)
    stock = create_stock(offer=offer, price=0)

    for i in range(booking_count):
        create_booking(user=user_having_booked, stock=stock, is_cancelled=False)

    repository.save(stock)


def _create_bookings_for_departement(bookings_by_departement):
    bookings = []

    offerer = create_offerer(name='Offerer', siren=222222222)
    venue = create_venue(offerer, departement_code='95', siret=22222222200001)
    offer = create_offer_with_thing_product(venue)
    stock = create_stock(offer=offer, price=10, quantity=1000)

    for departement_code, quantity in bookings_by_departement:
        user = create_user(departement_code=departement_code, email=f"user_in_{departement_code}@example.net")
        create_deposit(user, amount=500)
        bookings.append(create_booking(user=user, stock=stock, quantity=quantity))

    return bookings
