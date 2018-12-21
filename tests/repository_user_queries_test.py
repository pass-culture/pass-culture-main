from datetime import datetime

import pytest

from models import PcObject
from repository.user_queries import get_all_users_wallet_balances
from tests.conftest import clean_database
from utils.test_utils import create_user, create_offerer, create_venue, create_thing_offer, create_deposit, \
    create_stock, create_booking


@clean_database
@pytest.mark.standalone
def test_get_all_users_wallet_balances_sorted_by_user_id(app):
    # given
    user1 = create_user(email='user1@test.com')
    user2 = create_user(email='user2@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    stock1 = create_stock(price=20, offer=offer)
    stock2 = create_stock(price=30, offer=offer)
    stock3 = create_stock(price=40, offer=offer)
    PcObject.check_and_save(stock1, stock2, stock3, user1, user2)

    _create_balances_for_user1(stock1, stock2, stock3, user1, venue)
    _create_balances_for_user2(stock3, user2, venue)

    # when
    balances = get_all_users_wallet_balances()

    # then
    assert len(balances) == 2
    assert balances[0].user_id < balances[1].user_id


@clean_database
@pytest.mark.standalone
def test_get_all_users_wallet_ignores_users_with_no_deposits(app):
    # given
    user1 = create_user(email='user1@test.com')
    user2 = create_user(email='user2@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    stock3 = create_stock(price=40, offer=offer)
    PcObject.check_and_save(stock3, user1, user2)

    _create_balances_for_user2(stock3, user2, venue)

    # when
    balances = get_all_users_wallet_balances()

    # then
    assert len(balances) == 1


@clean_database
@pytest.mark.standalone
def test_get_all_users_wallet_balances_returns_current_balances(app):
    # given
    user1 = create_user(email='user1@test.com')
    user2 = create_user(email='user2@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    stock1 = create_stock(price=20, offer=offer)
    stock2 = create_stock(price=30, offer=offer)
    stock3 = create_stock(price=40, offer=offer)
    PcObject.check_and_save(stock1, stock2, stock3, user1, user2)

    _create_balances_for_user1(stock1, stock2, stock3, user1, venue)
    _create_balances_for_user2(stock3, user2, venue)

    # when
    balances = get_all_users_wallet_balances()

    # then
    assert balances[0].current_balance == 50
    assert balances[1].current_balance == 80


@clean_database
@pytest.mark.standalone
def test_get_all_users_wallet_balances_returns_real_balances(app):
    # given
    user1 = create_user(email='user1@test.com')
    user2 = create_user(email='user2@test.com')
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    stock1 = create_stock(price=20, offer=offer)
    stock2 = create_stock(price=30, offer=offer)
    stock3 = create_stock(price=40, offer=offer)
    PcObject.check_and_save(stock1, stock2, stock3, user1, user2)

    _create_balances_for_user1(stock1, stock2, stock3, user1, venue)
    _create_balances_for_user2(stock3, user2, venue)

    # when
    balances = get_all_users_wallet_balances()

    # then
    assert balances[0].real_balance == 90
    assert balances[1].real_balance == 200


def _create_balances_for_user2(stock3, user2, venue):
    deposit3 = create_deposit(user2, datetime.utcnow(), amount=200)
    booking4 = create_booking(user2, venue=venue, stock=stock3, quantity=3, is_cancelled=False, is_used=False)
    PcObject.check_and_save(deposit3, booking4)


def _create_balances_for_user1(stock1, stock2, stock3, user1, venue):
    deposit1 = create_deposit(user1, datetime.utcnow(), amount=100)
    deposit2 = create_deposit(user1, datetime.utcnow(), amount=50)
    booking1 = create_booking(user1, venue=venue, stock=stock1, quantity=1, is_cancelled=True, is_used=False)
    booking2 = create_booking(user1, venue=venue, stock=stock2, quantity=2, is_cancelled=False, is_used=True)
    booking3 = create_booking(user1, venue=venue, stock=stock3, quantity=1, is_cancelled=False, is_used=False)
    PcObject.check_and_save(deposit1, deposit2, booking1, booking2, booking3)
