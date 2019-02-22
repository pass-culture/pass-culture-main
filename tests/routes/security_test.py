import copy

import pytest

from models import PcObject, UserSession
from tests.conftest import clean_database
from tests.test_utils import create_user, API_URL, req, req_with_auth


@clean_database
@pytest.mark.standalone
def test_a_new_user_session_is_recorded_when_signing_in(app):
    # given
    user = create_user(email='user@example.com', password='toto123456789')
    PcObject.check_and_save(user)
    data = {'identifier': user.email, 'password': user.clearTextPassword}

    # when
    req.post(API_URL + '/users/signin', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    session = UserSession.query.filter_by(userId=user.id).first()
    assert session is not None


@clean_database
@pytest.mark.standalone
def test_an_existing_user_session_is_deleted_when_signing_out(app):
    # given
    user = create_user(email='test@mail.com', password='psswd123')
    PcObject.check_and_save(user)
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    assert auth_request.get(API_URL + '/bookings').status_code == 200

    # when
    auth_request.get(API_URL + '/users/signout')

    # then
    session = UserSession.query.filter_by(userId=user.id).first()
    assert session is None


@clean_database
@pytest.mark.standalone
def test_reusing_cookies_after_a_sign_out_is_unauthorized(app):
    # given
    user = create_user(email='test@mail.com', password='psswd123')
    PcObject.check_and_save(user)
    original_auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)
    spoofed_auth_request = copy.deepcopy(original_auth_request)

    assert original_auth_request.get(API_URL + '/bookings').status_code == 200
    spoofed_auth_request.cookies = copy.deepcopy(original_auth_request.cookies)
    original_auth_request.get(API_URL + '/users/signout')

    # when
    spoofed_response = spoofed_auth_request.get(API_URL + '/bookings')

    # then
    assert spoofed_response.status_code == 401
