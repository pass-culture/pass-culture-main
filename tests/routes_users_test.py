from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from models import PcObject
from models.db import db
from models.offerer import Offerer
from models.user import User
from models.user_offerer import UserOfferer, RightsType
from tests.conftest import clean_database
from utils.test_utils import API_URL, req, req_with_auth, create_thing_offer, create_user, create_offerer, create_venue, \
    create_stock_with_thing_offer, create_recommendation, create_deposit, create_booking

BASE_DATA = {
    'email': 'toto@btmx.fr',
    'publicName': 'Toto',
    'password': 'toto12345678',
    'contact_ok': 'true'
}

BASE_DATA_PRO = {
    'email': 'toto_pro@btmx.fr',
    'publicName': 'Toto Pro',
    'password': 'toto12345678',
    'contact_ok': 'true',
    'siren': '349974931',
    'address': '12 boulevard de Pesaro',
    'postalCode': '92000',
    'city': 'Nanterre',
    'name': 'Crédit Coopératif'
}


def assert_signup_error(data, err_field):
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert err_field in error


@pytest.mark.standalone
@clean_database
def test_signup_should_not_work_without_email(app):
    # Given
    data = BASE_DATA.copy()
    del (data['email'])

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'email' in error


@pytest.mark.standalone
@clean_database
def test_signup_should_not_work_with_invalid_email(app):
    # Given
    data = BASE_DATA.copy()
    data['email'] = 'toto'

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'email' in error


@pytest.mark.standalone
def test_signup_should_not_work_without_publicName():
    # Given
    data = BASE_DATA.copy()
    del (data['publicName'])

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'publicName' in error


@pytest.mark.standalone
def test_signup_should_not_work_with_publicName_too_short():
    # Given
    data = BASE_DATA.copy()
    data['publicName'] = 't'

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'publicName' in error


@pytest.mark.standalone
def test_signup_should_not_work_with_publicName_too_long():
    # Given
    data = BASE_DATA.copy()
    data['publicName'] = 'x' * 32

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'publicName' in error


@pytest.mark.standalone
def test_signup_should_not_work_without_password():
    # Given
    data = BASE_DATA.copy()
    del (data['password'])

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'password' in error


@pytest.mark.standalone
def test_signup_should_not_work_with_invalid_password():
    # Given
    data = BASE_DATA.copy()
    data['password'] = 'short'

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'password' in error


@pytest.mark.standalone
def test_signup_should_not_work_without_contact_ok():
    data = BASE_DATA.copy()
    del (data['contact_ok'])

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'contact_ok' in error


@pytest.mark.standalone
def test_signup_should_not_work_with_invalid_contact_ok():
    data = BASE_DATA.copy()
    data['contact_ok'] = 't'

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'contact_ok' in error


@pytest.mark.standalone
@clean_database
def test_signup(app):
    r_signup = req.post(API_URL + '/users/signup',
                        json=BASE_DATA)
    assert r_signup.status_code == 201
    assert 'Set-Cookie' in r_signup.headers


@pytest.mark.standalone
@clean_database
def test_signup_should_not_work_again_with_same_email(app):
    req.post(API_URL + '/users/signup',
             json=BASE_DATA)

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=BASE_DATA)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'email' in error


@pytest.mark.standalone
def test_get_profile_should_work_only_when_logged_in():
    r = req.get(API_URL + '/users/current')
    assert r.status_code == 401


@pytest.mark.standalone
@clean_database
def test_get_profile_should_return_the_users_profile_without_password_hash(app):
    user = create_user(email='toto@btmx.fr', public_name='Toto', departement_code='93', password='toto12345678')
    PcObject.check_and_save(user)
    r = req_with_auth(email='toto@btmx.fr',
                      password='toto12345678') \
        .get(API_URL + '/users/current')
    user_json = r.json()
    assert r.status_code == 200
    assert user_json['email'] == 'toto@btmx.fr'
    assert 'password' not in user_json


@pytest.mark.standalone
@clean_database
@patch('connectors.google_spreadsheet.get_authorized_emails_and_dept_codes')
def test_signup_should_not_work_for_user_not_in_exp_spreadsheet(get_authorized_emails_and_dept_codes, app):
    # Given
    get_authorized_emails_and_dept_codes.return_value = (['toto@email.com', 'other@email.com'], ['93', '93'])
    data = BASE_DATA.copy()
    data['email'] = 'unknown@unknown.com'

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'email' in error


# TODO
# def test_19_pro_signup_should_not_work_with_invalid_siren():
#    data = BASE_DATA_PRO.copy()
#    data['siren'] = '123456789'
#    assert_signup_error(data, 'siren')


@pytest.mark.standalone
@clean_database
def test_pro_signup_should_not_work_without_offerer_name(app):
    # Given
    data = BASE_DATA_PRO.copy()
    del (data['name'])

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'name' in error


@pytest.mark.standalone
def test_pro_signup_should_not_work_without_offerer_address():
    data = BASE_DATA_PRO.copy()
    del (data['address'])

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'address' in error


@pytest.mark.standalone
def test_pro_signup_should_not_work_without_offerer_city():
    data = BASE_DATA_PRO.copy()
    del (data['city'])

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'city' in error


@pytest.mark.standalone
def test_pro_signup_should_not_work_without_offerer_postal_code():
    data = BASE_DATA_PRO.copy()
    del (data['postalCode'])

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'postalCode' in error


@pytest.mark.standalone
def test_pro_signup_should_not_work_with_invalid_offerer_postal_code():
    data = BASE_DATA_PRO.copy()
    data['postalCode'] = '111'

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert 'postalCode' in error


@pytest.mark.standalone
@clean_database
def test_pro_signup_should_create_user_offerer_digital_venue_and_userOfferer(app):
    r_signup = req.post(API_URL + '/users/signup',
                        json=BASE_DATA_PRO)
    assert r_signup.status_code == 201
    assert 'Set-Cookie' in r_signup.headers
    user = User.query \
        .filter_by(email='toto_pro@btmx.fr') \
        .first()
    assert user is not None
    offerer = Offerer.query \
        .filter_by(siren='349974931') \
        .first()
    assert offerer is not None
    assert offerer.validationToken is not None
    assert len(offerer.managedVenues) == 1
    assert offerer.managedVenues[0].isVirtual
    user_offerer = UserOfferer.query \
        .filter_by(user=user,
                   offerer=offerer) \
        .first()
    assert user_offerer is not None
    assert user_offerer.validationToken is None
    assert user_offerer.rights == RightsType.admin


@clean_database
@pytest.mark.standalone
def test_pro_signup_with_existing_offerer(app):
    "should create user and userOfferer"
    json_offerer = {
        "name": "Test Offerer",
        "siren": "349974931",
        "address": "Test adresse",
        "postalCode": "75000",
        "city": "Paris"
    }
    offerer = Offerer(from_dict=json_offerer)
    PcObject.check_and_save(offerer)

    data = BASE_DATA_PRO.copy()
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)
    assert r_signup.status_code == 201
    assert 'Set-Cookie' in r_signup.headers
    user = User.query \
        .filter_by(email='toto_pro@btmx.fr') \
        .first()
    assert user is not None
    offerer = Offerer.query \
        .filter_by(siren='349974931') \
        .first()
    assert offerer is not None
    user_offerer = UserOfferer.query \
        .filter_by(user=user,
                   offerer=offerer) \
        .first()
    assert user_offerer is not None
    assert user_offerer.validationToken is not None
    assert user_offerer.rights == RightsType.editor


@clean_database
@pytest.mark.standalone
def test_user_should_have_its_wallet_balance(app):
    # Given
    user = create_user(email='wallet_test@email.com', public_name='Test', departement_code='93', password='testpsswd')
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


@pytest.mark.standalone
def test_user_with_isAdmin_true_and_canBookFreeOffers_raises_error():
    # Given
    user_json = {
        'email': 'pctest.isAdmin.canBook@btmx.fr',
        'publicName': 'IsAdmin CanBook',
        'password': 'toto12345678',
        'contact_ok': 'true',
        'isAdmin': True,
        'canBookFreeOffers': True
    }

    # When
    r_signup = req.post(API_URL + '/users/signup',
                        json=user_json)

    # Then
    assert r_signup.status_code == 400
    error = r_signup.json()
    assert error == {'canBookFreeOffers': ['Admin ne peut pas booker']}


@clean_database
@pytest.mark.standalone
def test_user_wallet_should_be_30_if_sum_deposit_50_and_one_booking_quantity_2_amount_10(app):
    # Given
    user = create_user(email='wallet_2_bookings_test@email.com', public_name='Test', departement_code='93',
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
    r_create = req_with_auth('wallet_2_bookings_test@email.com', 'testpsswd').get(API_URL + '/users/current')

    # Then
    wallet_balance = r_create.json()['wallet_balance']
    assert wallet_balance == 30


@clean_database
@pytest.mark.standalone
def test_get_current_user_returns_expenses(app):
    # Given
    user = create_user(email='wallet_2_bookings_test@email.com', public_name='Test', departement_code='93',
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
        'physical': {'max': 100, 'actual': 20},
        'digital': {'max': 200, 'actual': 0}
    }


@clean_database
@pytest.mark.standalone
def test_change_password_changes_the_current_user_password(app):
    # given
    user = create_user(email='user@test.com', password='testpsswd')
    PcObject.check_and_save(user)
    auth = req_with_auth(user.email, user.clearTextPassword)
    data = {'oldPassword': 'testpsswd', 'newPassword': 'n3wp4ssw0rd'}

    # when
    response = auth.post(API_URL + '/users/current/change-password', json=data)

    # then
    db.session.refresh(user)
    assert user.checkPassword('n3wp4ssw0rd') is True
    assert response.status_code == 204


@clean_database
@pytest.mark.standalone
def test_change_password_returns_bad_request_if_old_password_is_missing(app):
    # given
    user = create_user(email='user@test.com', password='testpsswd')
    PcObject.check_and_save(user)
    auth = req_with_auth(user.email, user.clearTextPassword)
    data = {'newPassword': 'n3wp4ssw0rd'}

    # when
    response = auth.post(API_URL + '/users/current/change-password', json=data)

    # then
    assert response.status_code == 400
    assert response.json()['oldPassword'] == ['Ancien mot de passe manquant']


@clean_database
@pytest.mark.standalone
def test_change_password_returns_bad_request_if_old_password_is_missing(app):
    # given
    user = create_user(email='user@test.com', password='testpsswd')
    PcObject.check_and_save(user)
    auth = req_with_auth(user.email, user.clearTextPassword)
    data = {'oldPassword': '0ldp4ssw0rd'}

    # when
    response = auth.post(API_URL + '/users/current/change-password', json=data)

    # then
    assert response.status_code == 400
    assert response.json()['newPassword'] == ['Nouveau mot de passe manquant']
