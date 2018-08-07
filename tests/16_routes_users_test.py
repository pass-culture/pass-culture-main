from datetime import datetime, timedelta

import pytest

from models import PcObject, Thing, Venue, Stock, Recommendation, Deposit, Booking, Offer
from pprint import pprint

from models.offerer import Offerer
from models.user import User
from models.user_offerer import UserOfferer, RightsType
from tests.conftest import clean_database
from utils.test_utils import API_URL, req, req_with_auth, create_thing_offer

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


def test_28_user_should_have_its_wallet_balance(app):
    # Given
    user = User()
    user.publicName = 'Test'
    user.email = 'wallet_test@email.com'
    user.setPassword('testpsswd')
    user.departementCode = '93'
    PcObject.check_and_save(user)

    offerer = Offerer()
    offerer.name = 'Test offerer'
    offerer.postalCode = '93000'
    offerer.address = '2 Test adress'
    offerer.city = 'Test city'
    offerer.siren = '999999987'
    PcObject.check_and_save(offerer)

    thing = Thing()
    thing.type = 'Book'
    thing.name = 'Test name'
    thing.extraData = {'author': 'Test Author'}
    PcObject.check_and_save(thing)

    venue = Venue()
    venue.name = 'Venue name'
    venue.bookingEmail = 'booking@email.com'
    venue.postalCode = '93000'
    venue.departementCode = '93'
    venue.address = '1 Test address'
    venue.city = 'Test city'
    venue.managingOffererId = offerer.id
    PcObject.check_and_save(venue)

    stock = Stock()
    stock.offererId = offerer.id
    stock.price = 5
    stock.venueId = venue.id
    stock.available = 50
    stock.offer = create_thing_offer()
    PcObject.check_and_save(stock)

    recommendation = Recommendation()
    recommendation.userId = user.id
    recommendation.thingId = thing.id
    PcObject.check_and_save(recommendation)

    deposit = Deposit()
    deposit.date = datetime.utcnow() - timedelta(minutes=2)
    deposit.amount = 10
    deposit.userId = user.id
    deposit.source = 'public'
    PcObject.check_and_save(deposit)

    deposit = Deposit()
    deposit.date = datetime.utcnow() - timedelta(minutes=2)
    deposit.amount = 10
    deposit.userId = user.id
    deposit.source = 'public'
    PcObject.check_and_save(deposit)

    booking = Booking()
    booking.stockId = stock.id
    booking.recommendationId = recommendation.id
    booking.userId = user.id
    booking.token = '2ALUY5'
    booking.amount = stock.price
    PcObject.check_and_save(booking)

    r_create = req_with_auth('wallet_test@email.com', 'testpsswd').get(API_URL + '/users/current')
    wallet_balance = r_create.json()['wallet_balance']
    print('rcreate', r_create)
    print('json', r_create.json())
    #Then
    assert wallet_balance == 15


def test_29_user_with_isAdmin_true_and_canBookFreeOffers_raises_error():
    user_json = {
        'email': 'pctest.isAdmin.canBook@btmx.fr',
        'publicName': 'IsAdmin CanBook',
        'password': 'toto12345678',
        'contact_ok': 'true',
        'isAdmin': True,
        'canBookFreeOffers': True
    }
    r_signup = req.post(API_URL + '/users/signup',
                                  json=user_json)

    assert r_signup.status_code == 400
    print(r_signup)
    error = r_signup.json()
    pprint(error)
    assert error == {'canBookFreeOffers': ['Admin ne peut pas booker']}


@clean_database
@pytest.mark.standalone
def test_30_user_wallet_should_be_30_if_sum_deposit_50_and_one_booking_quantity_2_amount_10(app):
    # Given
    user = User()
    user.publicName = 'Test'
    user.email = 'wallet_2_bookings_test@email.com'
    user.setPassword('testpsswd')
    user.departementCode = '93'
    PcObject.check_and_save(user)

    offerer = Offerer()
    offerer.name = 'Test offerer'
    offerer.postalCode = '93000'
    offerer.address = '2 Test adress'
    offerer.city = 'Test city'
    offerer.siren = '999199987'
    PcObject.check_and_save(offerer)

    thing = Thing()
    thing.type = 'Book'
    thing.name = 'Test name'
    thing.extraData = {'author': 'Test Author'}
    PcObject.check_and_save(thing)

    venue = Venue()
    venue.name = 'Venue name'
    venue.bookingEmail = 'booking@email.com'
    venue.postalCode = '93000'
    venue.departementCode = '93'
    venue.address = '1 Test address'
    venue.city = 'Test city'
    venue.managingOffererId = offerer.id
    PcObject.check_and_save(venue)

    stock = Stock()
    stock.offererId = offerer.id
    stock.price = 10
    stock.venueId = venue.id
    stock.available = 50
    stock.offer = create_thing_offer()
    PcObject.check_and_save(stock)

    recommendation = Recommendation()
    recommendation.userId = user.id
    recommendation.thingId = thing.id
    PcObject.check_and_save(recommendation)

    deposit = Deposit()
    deposit.date = datetime.utcnow() - timedelta(minutes=2)
    deposit.amount = 50
    deposit.userId = user.id
    deposit.source = 'public'
    PcObject.check_and_save(deposit)

    booking = Booking()
    booking.stockId = stock.id
    booking.recommendationId = recommendation.id
    booking.userId = user.id
    booking.token = '2ALUY5'
    booking.amount = stock.price
    booking.quantity = 2
    PcObject.check_and_save(booking)

    r_create = req_with_auth('wallet_2_bookings_test@email.com', 'testpsswd').get(API_URL + '/users/current')
    wallet_balance = r_create.json()['wallet_balance']
    print('json', r_create.json())
    print('wallet balance', wallet_balance)
    #Then
    assert wallet_balance == 30