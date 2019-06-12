from datetime import datetime, timedelta, MINYEAR

from models import PcObject
from repository.user_queries import get_all_users_wallet_balances, find_by_first_and_last_names_and_birth_date_and_email, \
    find_most_recent_beneficiary_creation_date
from tests.conftest import clean_database
from tests.test_utils import create_user, create_offerer, create_venue, create_offer_with_thing_product, create_deposit, \
    create_stock, create_booking, create_user_offerer


class GetAllUsersWalletBalancesTest:
    @clean_database
    def test_users_are_sorted_by_user_id(self, app):
        # given
        user1 = create_user(email='user1@test.com')
        user2 = create_user(email='user2@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(price=20, offer=offer)
        stock2 = create_stock(price=30, offer=offer)
        stock3 = create_stock(price=40, offer=offer)
        PcObject.save(stock1, stock2, stock3, user1, user2)

        _create_balances_for_user2(stock3, user2, venue)
        _create_balances_for_user1(stock1, stock2, stock3, user1, venue)

        # when
        balances = get_all_users_wallet_balances()

        # then
        assert len(balances) == 2
        assert balances[0].user_id < balances[1].user_id

    @clean_database
    def test_users_with_no_deposits_are_ignored(self, app):
        # given
        user1 = create_user(email='user1@test.com')
        user2 = create_user(email='user2@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock3 = create_stock(price=40, offer=offer)
        PcObject.save(stock3, user1, user2)

        _create_balances_for_user2(stock3, user2, venue)

        # when
        balances = get_all_users_wallet_balances()

        # then
        assert len(balances) == 1

    @clean_database
    def test_returns_current_balances(self, app):
        # given
        user1 = create_user(email='user1@test.com')
        user2 = create_user(email='user2@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(price=20, offer=offer)
        stock2 = create_stock(price=30, offer=offer)
        stock3 = create_stock(price=40, offer=offer)
        PcObject.save(stock1, stock2, stock3, user1, user2)

        _create_balances_for_user1(stock1, stock2, stock3, user1, venue)
        _create_balances_for_user2(stock3, user2, venue)

        # when
        balances = get_all_users_wallet_balances()

        # then
        assert balances[0].current_balance == 50
        assert balances[1].current_balance == 80

    @clean_database
    def test_returns_real_balances(self, app):
        # given
        user1 = create_user(email='user1@test.com')
        user2 = create_user(email='user2@test.com')
        offerer = create_offerer()
        venue = create_venue(offerer)
        offer = create_offer_with_thing_product(venue)
        stock1 = create_stock(price=20, offer=offer)
        stock2 = create_stock(price=30, offer=offer)
        stock3 = create_stock(price=40, offer=offer)
        PcObject.save(stock1, stock2, stock3, user1, user2)

        _create_balances_for_user1(stock1, stock2, stock3, user1, venue)
        _create_balances_for_user2(stock3, user2, venue)

        # when
        balances = get_all_users_wallet_balances()

        # then
        assert balances[0].real_balance == 90
        assert balances[1].real_balance == 200


class FindByFirstAndLastNamesAndEmailTest:
    @clean_database
    def test_returns_users_with_matching_criteria_ignoring_case(self, app):
        # given
        user1 = create_user(first_name="john", last_name='DOe', email='john@test.com',
                            date_of_birth=datetime(2000, 5, 1))
        user2 = create_user(first_name="jaNE", last_name='DOe', email='jane@test.com',
                            date_of_birth=datetime(2000, 3, 20))
        PcObject.save(user1, user2)

        # when
        users = find_by_first_and_last_names_and_birth_date_and_email('john', 'doe', datetime(2000, 5, 1), 'john@test.com')

        # then
        assert len(users) == 1
        assert users[0].email == 'john@test.com'

    @clean_database
    def test_returns_users_with_matching_criteria_ignoring_dash(self, app):
        # given
        user2 = create_user(first_name="jaNE", last_name='DOe', email='jane@test.com',
                            date_of_birth=datetime(2000, 3, 20))
        user1 = create_user(first_name="john-bob", last_name='doe', email='john.b@test.com',
                            date_of_birth=datetime(2000, 5, 1))
        PcObject.save(user1, user2)

        # when
        users = find_by_first_and_last_names_and_birth_date_and_email('johnbob', 'doe', datetime(2000, 5, 1), 'john.b@test.com')

        # then
        assert len(users) == 1
        assert users[0].email == 'john.b@test.com'

    @clean_database
    def test_returns_users_with_matching_criteria_ignoring_spaces(self, app):
        # given
        user2 = create_user(first_name="jaNE", last_name='DOe', email='jane@test.com',
                            date_of_birth=datetime(2000, 3, 20))
        user1 = create_user(first_name="john bob", last_name='doe', email='john.b@test.com',
                            date_of_birth=datetime(2000, 5, 1))
        PcObject.save(user1, user2)

        # when
        users = find_by_first_and_last_names_and_birth_date_and_email('johnbob', 'doe', datetime(2000, 5, 1), 'john.b@test.com')

        # then
        assert len(users) == 1
        assert users[0].email == 'john.b@test.com'

    @clean_database
    def test_returns_users_with_matching_criteria_ignoring_accents(self, app):
        # given
        user2 = create_user(first_name="jaNE", last_name='DOe', email='jane@test.com',
                            date_of_birth=datetime(2000, 3, 20))
        user1 = create_user(first_name="john bob", last_name='doe', email='john.b@test.com',
                            date_of_birth=datetime(2000, 5, 1))
        PcObject.save(user1, user2)

        # when
        users = find_by_first_and_last_names_and_birth_date_and_email('jöhn bób', 'doe', datetime(2000, 5, 1), 'john.b@test.com')

        # then
        assert len(users) == 1
        assert users[0].email == 'john.b@test.com'

    @clean_database
    def test_returns_nothing_if_one_criteria_does_not_match(self, app):
        # given
        user = create_user(first_name="Jean", last_name='DOe', date_of_birth=datetime(2000, 5, 1))
        PcObject.save(user)

        # when
        users = find_by_first_and_last_names_and_birth_date_and_email('john', 'doe', datetime(2000, 5, 1), 'johnny')

        # then
        assert not users


class FindMostRecentBeneficiaryCreationDateTest:
    @clean_database
    def test_returns_created_at_date_of_most_recent_beneficiary_user_that_has_an_demarche_simplifiee_application_id(self, app):
        # given
        now = datetime.utcnow()

        yesterday = now - timedelta(days=1)
        two_days_ago = now - timedelta(days=2)
        three_days_ago = now - timedelta(days=3)

        user1 = create_user(email='user1@test.com', date_created=yesterday, can_book_free_offers=False, demarcheSimplifieeApplicationId=1)
        user2 = create_user(email='user2@test.com', date_created=two_days_ago, can_book_free_offers=True, demarcheSimplifieeApplicationId=None)
        user3 = create_user(email='user3@test.com', date_created=three_days_ago, can_book_free_offers=True, demarcheSimplifieeApplicationId=3)
        offerer = create_offerer()
        user_offerer = create_user_offerer(user1, offerer)

        PcObject.save(user_offerer, user2, user3)

        # when
        most_recent_creation_date = find_most_recent_beneficiary_creation_date()

        # then
        assert most_recent_creation_date == three_days_ago

    @clean_database
    def test_returns_min_year_if_no_beneficiary_exist(self, app):
        # given
        yesterday = datetime.utcnow() - timedelta(days=1)
        user1 = create_user(email='user1@test.com', date_created=yesterday, can_book_free_offers=False)
        offerer = create_offerer()
        user_offerer = create_user_offerer(user1, offerer)
        PcObject.save(user_offerer)

        # when
        most_recent_creation_date = find_most_recent_beneficiary_creation_date()

        # then
        assert most_recent_creation_date == datetime(MINYEAR, 1, 1)


def _create_balances_for_user2(stock3, user2, venue):
    deposit3 = create_deposit(user2, datetime.utcnow(), amount=200)
    booking4 = create_booking(user2, venue=venue, stock=stock3, quantity=3, is_cancelled=False, is_used=False)
    PcObject.save(deposit3, booking4)


def _create_balances_for_user1(stock1, stock2, stock3, user1, venue):
    deposit1 = create_deposit(user1, datetime.utcnow(), amount=100)
    deposit2 = create_deposit(user1, datetime.utcnow(), amount=50)
    booking1 = create_booking(user1, venue=venue, stock=stock1, quantity=1, is_cancelled=True, is_used=False)
    booking2 = create_booking(user1, venue=venue, stock=stock2, quantity=2, is_cancelled=False, is_used=True)
    booking3 = create_booking(user1, venue=venue, stock=stock3, quantity=1, is_cancelled=False, is_used=False)
    PcObject.save(deposit1, deposit2, booking1, booking2, booking3)
