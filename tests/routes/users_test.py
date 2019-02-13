from datetime import datetime, timedelta

import pytest
import requests

from models import PcObject
from models.db import db
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import API_URL, req, req_with_auth, create_thing_offer, create_user, create_offerer, create_venue, \
    create_stock_with_thing_offer, create_recommendation, create_deposit, create_booking


@pytest.mark.standalone
@clean_database
def test_get_profile_should_work_only_when_logged_in(app):
    r = req.get(API_URL + '/users/current', headers={'origin': 'http://localhost:3000'})
    assert r.status_code == 401


@pytest.mark.standalone
@clean_database
def test_get_profile_should_return_the_users_profile_without_password_hash_and_password_reset_infos(app):
    user = create_user(public_name='Toto', departement_code='93', email='toto@btmx.fr', password='toto12345678')
    PcObject.check_and_save(user)
    r = req_with_auth(email='toto@btmx.fr', password='toto12345678') \
        .get(API_URL + '/users/current', headers={'origin': 'http://localhost:3000'})
    user_json = r.json()
    assert r.status_code == 200
    assert user_json['email'] == 'toto@btmx.fr'
    assert 'password' not in user_json
    assert 'resetPasswordToken' not in user_json
    assert 'resetPasswordTokenValidityLimit' not in user_json


@clean_database
@pytest.mark.standalone
def test_user_should_not_be_activated_by_default(app):
    # Given
    user = create_user(public_name='Test', departement_code='93', email='wallet_test@email.com', password='testpsswd')
    PcObject.check_and_save(user)

    # when
    r_profile = req_with_auth('wallet_test@email.com', 'testpsswd').get(API_URL + '/users/current')

    # Then
    assert r_profile.json()['wallet_is_activated'] == False


@clean_database
@pytest.mark.standalone
def test_user_wallet_should_be_marked_as_activated_when_there_is_a_deposit(app):
    # Given
    user = create_user(public_name='Test', departement_code='93', email='wallet_test@email.com', password='testpsswd')
    PcObject.check_and_save(user)

    deposit_date = datetime.utcnow() - timedelta(minutes=2)
    deposit = create_deposit(user, deposit_date, amount=10)
    PcObject.check_and_save(deposit)

    # when
    r_profile = req_with_auth('wallet_test@email.com', 'testpsswd').get(API_URL + '/users/current')

    # Then
    assert r_profile.json()['wallet_is_activated'] == True


@clean_database
@pytest.mark.standalone
def test_user_should_have_its_wallet_balance(app):
    # Given
    user = create_user(public_name='Test', departement_code='93', email='wallet_test@email.com', password='testpsswd')
    PcObject.check_and_save(user)

    offerer = create_offerer('999199987', '2 Test adress', 'Test city', '93000', 'Test offerer')
    PcObject.check_and_save(offerer)

    venue = create_venue(offerer)
    PcObject.check_and_save(venue)

    thing_offer = create_thing_offer(venue=None)
    stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=5)
    PcObject.check_and_save(stock)

    recommendation = create_recommendation(thing_offer, user)
    PcObject.check_and_save(recommendation)

    deposit_1_date = datetime.utcnow() - timedelta(minutes=2)
    deposit_1 = create_deposit(user, deposit_1_date, amount=10)
    PcObject.check_and_save(deposit_1)

    deposit_2_date = datetime.utcnow() - timedelta(minutes=2)
    deposit_2 = create_deposit(user, deposit_2_date, amount=10)
    PcObject.check_and_save(deposit_2)

    booking = create_booking(user, stock, venue, recommendation, quantity=1)
    PcObject.check_and_save(booking)

    r_create = req_with_auth('wallet_test@email.com', 'testpsswd').get(API_URL + '/users/current')

    # when
    wallet_balance = r_create.json()['wallet_balance']

    # Then
    assert wallet_balance == 15


@clean_database
@pytest.mark.standalone
def test_get_current_user_returns_expenses(app):
    # Given
    user = create_user(public_name='Test', departement_code='93', email='wallet_2_bookings_test@email.com',
                       password='testpsswd')
    offerer = create_offerer('999199987', '2 Test adress', 'Test city', '93000', 'Test offerer')
    venue = create_venue(offerer)
    thing_offer = create_thing_offer(venue=None)
    stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=10)
    recommendation = create_recommendation(thing_offer, user)
    deposit_date = datetime.utcnow() - timedelta(minutes=2)
    deposit = create_deposit(user, deposit_date, amount=50)
    booking = create_booking(user, stock, venue, recommendation, quantity=2)

    PcObject.check_and_save(deposit)
    PcObject.check_and_save(booking)

    # When
    response = req_with_auth('wallet_2_bookings_test@email.com', 'testpsswd').get(API_URL + '/users/current')

    # Then
    expenses = response.json()['expenses']
    assert expenses == {
        'all': {'max': 500, 'actual': 20},
        'physical': {'max': 200, 'actual': 20},
        'digital': {'max': 200, 'actual': 0}
    }


@pytest.mark.standalone
@clean_database
def test_patch_user_returns_200_for_allowed_changes(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)

    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')
    data = {'publicName': 'plop', 'email': 'new@email.com', 'postalCode': '93020', 'phoneNumber': '0612345678',
            'departementCode': '97'}

    # when
    response = auth_request.patch(API_URL + '/users/current', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    db.session.refresh(user)
    assert response.status_code == 200
    assert response.json()['id'] == humanize(user.id)
    assert response.json()['publicName'] == user.publicName
    assert user.publicName == data['publicName']
    assert response.json()['email'] == user.email
    assert user.email == data['email']
    assert response.json()['postalCode'] == user.postalCode
    assert user.postalCode == data['postalCode']
    assert response.json()['phoneNumber'] == user.phoneNumber
    assert user.phoneNumber == data['phoneNumber']
    assert response.json()['departementCode'] == user.departementCode
    assert user.departementCode == data['departementCode']
    assert 'expenses' in response.json()


@pytest.mark.standalone
@clean_database
def test_patch_user_returns_400_when_not_allowed_changes(app):
    # given
    user = create_user(can_book_free_offers=True, password='p@55sw0rd', is_admin=False)
    PcObject.check_and_save(user)

    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')
    data = {'isAdmin': True, 'canBookFreeOffers': False, 'firstName': 'Jean', 'lastName': 'Martin',
            'dateCreated': '2018-08-01 12:00:00', 'resetPasswordToken': 'abc',
            'resetPasswordTokenValidityLimit': '2020-07-01 12:00:00'}

    # when
    response = auth_request.patch(API_URL + '/users/current', json=data)

    # then
    db.session.refresh(user)
    assert response.status_code == 400
    for key in data:
        assert response.json()[key] == ['Vous ne pouvez pas changer cette information']


@pytest.mark.standalone
@clean_database
def test_get_current_user_returns_400_when_header_not_in_whitelist(app):
    # given
    user = create_user(email='e@mail.com', can_book_free_offers=True, password='p@55sw0rd', is_admin=False)
    PcObject.check_and_save(user)

    # when
    response = requests.get(API_URL + '/users/current', auth=('e@mail.com', 'p@55sw0rd'),
                            headers={'origin': 'random.header.fr'})

    # then
    assert response.status_code == 400
    assert response.json()['global'] == ['Header non autorisé']
