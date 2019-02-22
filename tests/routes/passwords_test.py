from datetime import datetime, timedelta

import pytest

from domain.password import RESET_PASSWORD_TOKEN_LENGTH
from models import PcObject
from models.db import db
from tests.conftest import clean_database
from tests.test_utils import API_URL, req, req_with_auth, create_user


@clean_database
@pytest.mark.standalone
def test_post_change_password_changes_the_current_user_password(app):
    # given
    user = create_user(email='user@test.com', password='testpsswd')
    PcObject.check_and_save(user)
    auth = req_with_auth(user.email, user.clearTextPassword)
    data = {'oldPassword': 'testpsswd', 'newPassword': 'N3W_p4ssw0rd'}

    # when
    response = auth.post(API_URL + '/users/current/change-password', json=data)

    # then
    db.session.refresh(user)
    assert user.checkPassword('N3W_p4ssw0rd') is True
    assert response.status_code == 204


@clean_database
@pytest.mark.standalone
def test_post_change_password_returns_bad_request_if_old_password_is_missing(app):
    # given
    user = create_user(email='user@test.com', password='testpsswd')
    PcObject.check_and_save(user)
    auth = req_with_auth(user.email, user.clearTextPassword)
    data = {'newPassword': 'N3W_p4ssw0rd'}

    # when
    response = auth.post(API_URL + '/users/current/change-password', json=data)

    # then
    assert response.status_code == 400
    assert response.json()['oldPassword'] == ['Ancien mot de passe manquant']


@clean_database
@pytest.mark.standalone
def test_post_change_password_returns_bad_request_if_old_password_is_missing(app):
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


@clean_database
@pytest.mark.standalone
def test_post_change_password_returns_bad_request_if_the_new_password_is_not_strong_enough(app):
    # given
    user = create_user(email='user@test.com', password='testpsswd')
    PcObject.check_and_save(user)
    auth = req_with_auth(user.email, user.clearTextPassword)
    data = {'oldPassword': '0ldp4ssw0rd', 'newPassword': 'weakpassword'}

    # when
    response = auth.post(API_URL + '/users/current/change-password', json=data)

    # then
    assert response.status_code == 400
    assert response.json()['newPassword'] == [
        'Le mot de passe doit faire au moins 12 caractères et contenir à minima '
        '1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;'
    ]


@clean_database
@pytest.mark.standalone
def test_post_for_password_token_records_a_new_password_token_if_email_is_known(app):
    # given
    data = {'email': 'bobby@test.com'}
    user = create_user(email='bobby@test.com')
    PcObject.check_and_save(user)

    # when
    response = req.post(API_URL + '/users/reset-password', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    db.session.refresh(user)
    assert response.status_code == 204
    assert len(user.resetPasswordToken) == RESET_PASSWORD_TOKEN_LENGTH
    now = datetime.utcnow()
    assert (now + timedelta(hours=23)) < user.resetPasswordTokenValidityLimit < (now + timedelta(hours=25))


@clean_database
@pytest.mark.standalone
def test_post_for_password_token_returns_no_content_if_email_is_unknown(app):
    # given
    data = {'email': 'unknown.user@test.com'}

    # when
    response = req.post(API_URL + '/users/reset-password', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    assert response.status_code == 204


@clean_database
@pytest.mark.standalone
def test_post_for_password_token_returns_bad_request_if_email_is_empty(app):
    # given
    data = {'email': ''}

    # when
    response = req.post(API_URL + '/users/reset-password', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    assert response.status_code == 400
    assert response.json()['email'] == ['L\'email renseigné est vide']


@clean_database
@pytest.mark.standalone
def test_post_for_password_token_returns_bad_request_if_email_is_missing(app):
    # given
    data = {}

    # when
    response = req.post(API_URL + '/users/reset-password', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    assert response.status_code == 400
    assert response.json()['email'] == ['L\'email est manquant']


@clean_database
@pytest.mark.standalone
def test_post_new_password_changes_the_user_password(app):
    # given
    user = create_user(password='0ld_p455w0rd', reset_password_token='KL89PBNG51')
    PcObject.check_and_save(user)

    data = {
        'token': 'KL89PBNG51',
        'newPassword': 'N3W_p4ssw0rd'
    }

    # when
    response = req.post(API_URL + '/users/new-password', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    db.session.refresh(user)
    assert response.status_code == 204
    assert user.checkPassword('N3W_p4ssw0rd')


@clean_database
@pytest.mark.standalone
def test_post_new_password_remove_the_reset_token_and_the_validity_date(app):
    # given
    user = create_user(password='0ld_p455w0rd', reset_password_token='KL89PBNG51')
    PcObject.check_and_save(user)

    data = {
        'token': 'KL89PBNG51',
        'newPassword': 'N3W_p4ssw0rd'
    }

    # when
    req.post(API_URL + '/users/new-password', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    db.session.refresh(user)
    assert user.resetPasswordToken is None
    assert user.resetPasswordTokenValidityLimit is None


@clean_database
@pytest.mark.standalone
def test_post_new_password_returns_bad_request_if_the_token_is_outdated(app):
    # given
    user = create_user(password='0ld_p455w0rd', reset_password_token='KL89PBNG51',
                       reset_password_token_validity_limit=datetime.utcnow() - timedelta(days=2))
    PcObject.check_and_save(user)

    data = {
        'token': 'KL89PBNG51',
        'newPassword': 'N3W_p4ssw0rd'
    }

    # when
    response = req.post(API_URL + '/users/new-password', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    assert response.status_code == 400
    assert response.json()['token'] == [
        'Votre lien de changement de mot de passe est périmé. Veuillez effecture une nouvelle demande.'
    ]


@clean_database
@pytest.mark.standalone
def test_post_new_password_returns_bad_request_if_the_token_is_unknown(app):
    # given
    user = create_user(password='0ld_p455w0rd', reset_password_token='KL89PBNG51')
    PcObject.check_and_save(user)

    data = {
        'token': 'AZER1QSDF2',
        'newPassword': 'N3W_p4ssw0rd'
    }

    # when
    response = req.post(API_URL + '/users/new-password', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    assert response.status_code == 400
    assert response.json()['token'] == [
        'Votre lien de changement de mot de passe est invalide.'
    ]


@clean_database
@pytest.mark.standalone
def test_post_new_password_returns_bad_request_if_the_token_is_missing(app):
    # given
    user = create_user(password='0ld_p455w0rd', reset_password_token='KL89PBNG51')
    PcObject.check_and_save(user)

    data = {'newPassword': 'N3W_p4ssw0rd'}

    # when
    response = req.post(API_URL + '/users/new-password', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    assert response.status_code == 400
    assert response.json()['token'] == [
        'Votre lien de changement de mot de passe est invalide.'
    ]


@clean_database
@pytest.mark.standalone
def test_post_new_password_returns_bad_request_if_the_new_password_is_missing(app):
    # given
    user = create_user(password='0ld_p455w0rd', reset_password_token='KL89PBNG51')
    PcObject.check_and_save(user)

    data = {'token': 'KL89PBNG51'}

    # when
    response = req.post(API_URL + '/users/new-password', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    assert response.status_code == 400
    assert response.json()['newPassword'] == [
        'Vous devez renseigner un nouveau mot de passe.'
    ]


@clean_database
@pytest.mark.standalone
def test_post_new_password_returns_bad_request_if_the_new_password_is_not_strong_enough(app):
    # given
    user = create_user(password='0ld_p455w0rd', reset_password_token='KL89PBNG51')
    PcObject.check_and_save(user)

    data = {'token': 'KL89PBNG51', 'newPassword': 'weak_password'}

    # when
    response = req.post(API_URL + '/users/new-password', json=data, headers={'origin': 'http://localhost:3000'})

    # then
    assert response.status_code == 400
    assert response.json()['newPassword'] == [
        'Le mot de passe doit faire au moins 12 caractères et contenir à minima '
        '1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;'
    ]
