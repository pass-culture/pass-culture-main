from datetime import datetime, timedelta

import pytest

from models import PcObject, Thing, Venue, Stock, Recommendation, Deposit, Booking, Offer
from pprint import pprint

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
    pprint(error)
    assert err_field in error


def test_10_signup_should_not_work_without_email():
    data = BASE_DATA.copy()
    del(data['email'])
    assert_signup_error(data, 'email')


def test_10_signup_should_not_work_with_invalid_email():
    data = BASE_DATA.copy()
    data['email'] = 'toto'
    assert_signup_error(data, 'email')


def test_10_signup_should_not_work_without_publicName():
    data = BASE_DATA.copy()
    del(data['publicName'])
    assert_signup_error(data, 'publicName')


def test_10_signup_should_not_work_with_invalid_publicName():
    data = BASE_DATA.copy()
    data['publicName'] = 't'
    assert_signup_error(data, 'publicName')
    data = BASE_DATA.copy()
    data['publicName'] = 'x'*32
    assert_signup_error(data, 'publicName')


def test_10_signup_should_not_work_without_password():
    data = BASE_DATA.copy()
    del(data['password'])
    assert_signup_error(data, 'password')


def test_10_signup_should_not_work_with_invalid_password():
    data = BASE_DATA.copy()
    data['password'] = 'short'
    assert_signup_error(data, 'password')


def test_10_signup_should_not_work_without_contact_ok():
    data = BASE_DATA.copy()
    del(data['contact_ok'])
    assert_signup_error(data, 'contact_ok')


def test_10_signup_should_not_work_with_invalid_contact_ok():
    data = BASE_DATA.copy()
    data['contact_ok'] = 't'
    assert_signup_error(data, 'contact_ok')


def test_11_signup():
    r_signup = req.post(API_URL + '/users/signup',
                        json=BASE_DATA)
    print(r_signup.json())
    assert r_signup.status_code == 201
    assert 'Set-Cookie' in r_signup.headers


def test_12_signup_should_not_work_again_with_same_email():
    assert_signup_error(BASE_DATA, 'email')


def test_13_get_profile_should_work_only_when_logged_in():
    r = req.get(API_URL + '/users/current')
    assert r.status_code == 401


#def test_14_get_profile_should_not_work_if_account_is_not_validated():
#    r = req_with_auth(email='toto@btmx.fr',
#                      password='toto12345678')\
#                    .get(API_URL + '/users/current')
#    assert r.status_code == 401
#    assert 'pas validé' in r.json()['identifier']


#def test_15_should_not_be_able_to_validate_user_with_wrong_token():
#    r = req_with_auth(email='toto@btmx.fr',
#                      password='toto12345678')\
#                 .get(API_URL + '/validate?modelNames=User&token=123')
#    assert r.status_code == 404


#def test_16_should_be_able_to_validate_user(app):
#    token = User.query\
#                .filter(User.validationToken != None)\
#                .first().validationToken
#    r = req_with_auth().get(API_URL + '/validate?modelNames=User&token='+token)
#    assert r.status_code == 202


def test_17_get_profile_should_return_the_users_profile_without_password_hash():
    r = req_with_auth(email='toto@btmx.fr',
                      password='toto12345678')\
                 .get(API_URL + '/users/current')
    user = r.json()
    print(user)
    assert r.status_code == 200
    assert user['email'] == 'toto@btmx.fr'
    assert 'password' not in user


def test_18_signup_should_not_work_for_user_not_in_exp_spreadsheet():
    data = BASE_DATA.copy()
    data['email'] = 'unknown@unknown.com'
    assert_signup_error(data, 'email')

#TODO
#def test_19_pro_signup_should_not_work_with_invalid_siren():
#    data = BASE_DATA_PRO.copy()
#    data['siren'] = '123456789'
#    assert_signup_error(data, 'siren')


def test_19_pro_signup_should_not_work_without_offerer_name():
    data = BASE_DATA_PRO.copy()
    del(data['name'])
    assert_signup_error(data, 'name')


def test_20_pro_signup_should_not_work_without_offerer_address():
    data = BASE_DATA_PRO.copy()
    del(data['address'])
    assert_signup_error(data, 'address')


def test_21_pro_signup_should_not_work_without_offerer_city():
    data = BASE_DATA_PRO.copy()
    del(data['city'])
    assert_signup_error(data, 'city')


def test_22_pro_signup_should_not_work_without_offerer_postal_code():
    data = BASE_DATA_PRO.copy()
    del(data['postalCode'])
    assert_signup_error(data, 'postalCode')


def test_23_pro_signup_should_not_work_with_invalid_offerer_postal_code():
    data = BASE_DATA_PRO.copy()
    data['postalCode'] = '111'
    assert_signup_error(data, 'postalCode')


offerer_id = None


def test_24_pro_signup_should_create_user_offerer_and_userOfferer(app):
    global offerer_id
    r_signup = req.post(API_URL + '/users/signup',
                        json=BASE_DATA_PRO)
    assert r_signup.status_code == 201
    assert 'Set-Cookie' in r_signup.headers
    user = User.query\
                         .filter_by(email='toto_pro@btmx.fr')\
                         .first()
    assert user is not None
    offerer = Offerer.query\
                               .filter_by(siren='349974931')\
                               .first()
    assert offerer is not None
    assert offerer.validationToken is not None
    offerer_id = offerer.id
    user_offerer = UserOfferer.query\
                                        .filter_by(user=user,
                                                   offerer=offerer)\
                                        .first()
    assert user_offerer is not None
    assert user_offerer.validationToken is None
    assert user_offerer.rights == RightsType.admin


def test_25_should_not_be_able_to_validate_offerer_with_wrong_token():
    r = req_with_auth(email='toto_pro@btmx.fr',
                      password='toto12345678')\
                 .get(API_URL + '/validate?modelNames=Offerer&token=123')
    assert r.status_code == 404


def test_26_validate_offerer(app):
    global offerer_id
    token = Offerer.query\
                             .filter_by(id=offerer_id)\
                             .first().validationToken
    r = req.get(API_URL + '/validate?modelNames=Offerer&token='+token)
    assert r.status_code == 202
    offerer = Offerer.query\
                               .filter_by(id=offerer_id)\
                               .first()
    assert offerer.validationToken is None


def test_27_pro_signup_with_existing_offerer(app):
    "should create user and userOfferer"
    json_offerer = {
            "name": "Test Offerer",
            "siren": "418166096",
            "address": "Test adresse",
            "postalCode": "75000",
            "city": "Paris"
    }
    offerer = Offerer(from_dict=json_offerer)
    offerer.save()


    data = BASE_DATA_PRO.copy()
    data['email'] = 'toto_pro2@btmx.fr'
    data['siren'] = '418166096'
    r_signup = req.post(API_URL + '/users/signup',
                        json=data)
    assert r_signup.status_code == 201
    assert 'Set-Cookie' in r_signup.headers
    user = User.query\
                         .filter_by(email='toto_pro2@btmx.fr')\
                         .first()
    assert user is not None
    offerer = Offerer.query\
                               .filter_by(siren='418166096')\
                               .first()
    assert offerer is not None
    user_offerer = UserOfferer.query\
                                        .filter_by(user=user,
                                                   offerer=offerer)\
                                        .first()
    assert user_offerer is not None
    assert user_offerer.validationToken is not None
    assert user_offerer.rights == RightsType.editor


@clean_database
@pytest.mark.standalone
def test_28_user_should_have_its_wallet_balance(app):
    # Given
    user = create_user('wallet_test@email.com', 'Test', '93', password='testpsswd')
    PcObject.check_and_save(user)

    offerer = create_offerer('999199987', '2 Test adress', 'Test city', '93000', 'Test offerer')
    PcObject.check_and_save(offerer)

    venue = create_venue(offerer,'booking@email.com', '1 Test address', '93000', 'Test city', 'Venue name', '93')
    PcObject.check_and_save(venue)

    thing_offer = create_thing_offer()
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

    booking = create_booking(user, stock, recommendation, quantity=1)
    PcObject.check_and_save(booking)

    r_create = req_with_auth('wallet_test@email.com', 'testpsswd').get(API_URL + '/users/current')
    wallet_balance = r_create.json()['wallet_balance']
    #Then
    assert wallet_balance == 15


@pytest.mark.standalone
def test_29_user_with_isAdmin_true_and_canBookFreeOffers_raises_error():
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
    pprint(error)
    assert error == {'canBookFreeOffers': ['Admin ne peut pas booker']}


@clean_database
@pytest.mark.standalone
def test_30_user_wallet_should_be_30_if_sum_deposit_50_and_one_booking_quantity_2_amount_10(app):
    # Given
    user = create_user('wallet_2_bookings_test@email.com', 'Test', '93', password='testpsswd')
    PcObject.check_and_save(user)

    offerer = create_offerer('999199987', '2 Test adress', 'Test city', '93000', 'Test offerer')
    PcObject.check_and_save(offerer)

    venue = create_venue(offerer,'booking@email.com', '1 Test address', '93000', 'Test city', 'Venue name', '93')
    PcObject.check_and_save(venue)

    thing_offer = create_thing_offer()
    stock = create_stock_with_thing_offer(offerer, venue, thing_offer, price=10)
    PcObject.check_and_save(stock)

    recommendation = create_recommendation(thing_offer, user)
    PcObject.check_and_save(recommendation)

    deposit_date = datetime.utcnow() - timedelta(minutes=2)
    deposit = create_deposit(user, deposit_date, amount=50)
    PcObject.check_and_save(deposit)

    booking = create_booking(user, stock, recommendation, quantity=2)
    PcObject.check_and_save(booking)

    # When
    r_create = req_with_auth('wallet_2_bookings_test@email.com', 'testpsswd').get(API_URL + '/users/current')

    # Then
    wallet_balance = r_create.json()['wallet_balance']
    assert wallet_balance == 30