import os
from datetime import datetime

import pytest
import requests

from models import PcObject
from tests.conftest import clean_database
from utils.test_utils import API_URL, create_user, req_with_auth, create_user_offerer, \
    create_offerer

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
def test_check_user_is_admin_returns_403_when_user_is_not_admin(app):
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
def test_check_user_is_admin_returns_200_when_user_is_admin(app):
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
def test_check_user_is_admin_returns_403_when_user_is_structure_admin_but_not_admin(app):
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
