import os
from datetime import datetime

import pytest
import requests

from models import PcObject
from tests.conftest import clean_database
from utils.test_utils import API_URL, create_user, req_with_auth, create_user_offerer, \
    create_offerer, create_venue

TOKEN = os.environ.get('EXPORT_TOKEN')



@pytest.mark.standalone
@clean_database
def test_export_model_returns_200_when_given_model_is_known(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/exports/models/%s?token=%s' % ('Venue', TOKEN))

    # then
    assert response.status_code == 200


@pytest.mark.standalone
@clean_database
def test_export_model_returns_400_when_given_model_is_not_exportable(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/exports/models/%s?token=%s' % ('VersionedMixin', TOKEN))

    # then
    assert response.status_code == 400
    assert response.json()['global'] == ['Classe non exportable : VersionedMixin']


@pytest.mark.standalone
@clean_database
def test_export_model_returns_bad_request_if_no_token_provided(app):
    # when
    response = requests.get(API_URL + '/exports/models/%s' % ('Venue'), headers={'origin':
       'http://localhost:3000'})

    # then
    assert response.status_code == 400


@pytest.mark.standalone
@clean_database
def test_export_model_returns_400_when_given_model_is_unknown(app):
    # given
    user = create_user(password='p@55sw0rd')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    # when
    response = auth_request.get(API_URL + '/exports/models/%s?token=%s' % ('RandomStuff', TOKEN))

    # then
    assert response.status_code == 400
    assert response.json()['global'] == ['Classe inconnue : RandomStuff']


@pytest.mark.standalone
@clean_database
def test_check_pending_validation_returns_403_when_user_is_not_admin(app):
    #given
    user = create_user(password='p@55sw0rd', is_admin=False)
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.get(API_URL + '/exports/pending_validation')

    #then
    assert response.status_code == 403


@pytest.mark.standalone
@clean_database
def test_check_pending_validation_returns_200_when_user_is_admin(app):
    #given
    user = create_user(can_book_free_offers=False, password='p@55sw0rd', is_admin=True)
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.get(API_URL + '/exports/pending_validation')

    #then
    assert response.status_code == 200


@pytest.mark.standalone
@clean_database
def test_check_pending_validation_returns_403_when_user_is_structure_admin_but_not_admin(app):
    #given
    user = create_user(can_book_free_offers=False, password='p@55sw0rd', is_admin=False)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    PcObject.check_and_save(user_offerer)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.get(API_URL + '/exports/pending_validation')

    #then
    assert response.status_code == 403


@pytest.mark.standalone
@clean_database
def test_check_pending_validation_return_200_and_validation_token(app):
    #given
    user = create_user(can_book_free_offers=False, password='p@55sw0rd', is_admin=True)
    user_pro = create_user(email='user0@test.com', can_book_free_offers=False, password='p@55sw0rd', is_admin=False)
    offerer = create_offerer(validation_token="first_token")
    user_offerer = create_user_offerer(user_pro, offerer, is_admin=True, validation_token="a_token")

    PcObject.check_and_save(user_offerer,user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.get(API_URL + '/exports/pending_validation')

    #then
    assert response.status_code == 200
    assert response.json()[0]["validationToken"] == "first_token"
    assert response.json()[0]["UserOfferers"][0]["validationToken"] == "a_token"


@pytest.mark.standalone
@clean_database
def test_get_venues_returns_403_when_user_is_not_admin(app):
    #given
    data={}
    user = create_user(password='p@55sw0rd', is_admin=False)
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.post(API_URL + '/exports/venues', json=data)

    #then
    assert response.status_code == 403


@pytest.mark.standalone
@clean_database
def test_get_venues_returns_200_when_user_is_admin(app):
    #given
    data={}
    user = create_user(password='p@55sw0rd', is_admin=True, can_book_free_offers=False)
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.post(API_URL + '/exports/venues', json=data)

    #then
    assert response.status_code == 200


@pytest.mark.standalone
@clean_database
def test_get_venues_returns_403_when_user_is_structure_admin_but_not_admin(app):
    #given
    data={}
    user = create_user(is_admin=False, can_book_free_offers=False)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    venue = create_venue(offerer)
    PcObject.check_and_save(user_offerer, venue)
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    #when
    response = auth_request.post(API_URL + '/exports/venues', json=data)

    #then
    assert response.status_code == 403


@pytest.mark.standalone
@clean_database
def test_get_venues_return_200_and_venue_with_params(app):
    #given
    data={
        "has_validated_offerer": True,
        "dpt": ["93","67"],
        "has_siret": True,
        "is_virtual": False,
        "is_validated": True
    }

    user = create_user(password='p@55sw0rd', is_admin=True, can_book_free_offers=False)
    validated_offerer = create_offerer()
    not_validated_offerer = create_offerer(validation_token="here is a token", siren="123456798")
    
    venue93 = create_venue(validated_offerer, name='venue93', postal_code='93100', siret="12345678912310")
    venue67 = create_venue(validated_offerer, name='venue67', postal_code='67100', siret="12345678912311")
    venue34 = create_venue(validated_offerer, name='venue34', postal_code='34100', siret="12345678912312")
    venue_without_siret = create_venue(validated_offerer, name='venue_without_siret', comment="here is a comment" , siret=None)
    venue_virtual = create_venue(validated_offerer, name='venue_virtual', siret=None, is_virtual=True)
    venue_not_validated = create_venue(validated_offerer, name='venue_not_validated', 
        validation_token="here is a validation_token", siret="12345678912315")

    venue_with_not_validated_offerer = create_venue(not_validated_offerer, name='venue_with_not_validated_offerer', siret="12345678912316")

    PcObject.check_and_save(user, venue93, venue67, venue34, venue_without_siret, venue_virtual, venue_not_validated, venue_with_not_validated_offerer)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.post(API_URL + '/exports/venues', json=data)

    #then
    venue_names = list(map(lambda x: x['name'], response.json()))

    assert response.status_code == 200
    assert venue93.name in venue_names
    assert venue67.name in venue_names
    assert venue34.name not in venue_names
    assert venue_without_siret.name not in venue_names
    assert venue_virtual.name not in venue_names
    assert venue_not_validated.name not in venue_names
    assert venue_with_not_validated_offerer.name not in venue_names



@pytest.mark.standalone
@clean_database
def test_get_venues_return_error_when_date_param_is_wrong(app):
    #given
    wrong_date = "I\'m not a valid date"
    data = {'from_date': wrong_date}
    user = create_user(password='p@55sw0rd', is_admin=True, can_book_free_offers=False)

    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

    #when
    response = auth_request.post(API_URL + '/exports/venues', json=data)

    #then
    assert response.status_code == 400
    assert response.json()['date_format'] == ['to_date and from_date are of type yyyy-mm-dd'] 
    