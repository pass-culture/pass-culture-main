import secrets

import pytest

from models import Offerer, PcObject
from models.db import db
from tests.conftest import clean_database
from utils.test_utils import req, create_user, req_with_auth, API_URL, create_offerer, create_user_offerer, create_venue


@clean_database
@pytest.mark.standalone
def test_should_not_be_able_to_validate_offerer_with_non_existing_token(app):
    r = req_with_auth(email='toto_pro@btmx.fr', password='toto12345678') \
        .get(API_URL + '/validate?modelNames=Offerer&token=123')
    assert r.status_code == 404


@clean_database
@pytest.mark.standalone
def test_validate_offerer(app):
    # Given
    offerer_token = secrets.token_urlsafe(20)
    offerer = create_offerer('349974931', '12 boulevard de Pesaro', 'Nanterre', '92000', 'Crédit Coopératif',
                             validation_token=offerer_token)
    user = create_user()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    PcObject.check_and_save(offerer, user_offerer)
    offerer_id = offerer.id
    del (offerer)

    token = Offerer.query \
        .filter_by(id=offerer_id) \
        .first().validationToken

    # When
    r = req.get(API_URL + '/validate?modelNames=Offerer&token=' + token, headers={'origin': 'http://localhost:3000'})

    # Then
    assert r.status_code == 202
    offerer = Offerer.query \
        .filter_by(id=offerer_id) \
        .first()
    assert offerer.isValidated


@clean_database
@pytest.mark.standalone
def test_validate_venue_with_right_validation_token_sets_validation_token_to_none(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    venue.generate_validation_token()
    PcObject.check_and_save(venue)

    token = venue.validationToken

    # When
    r = req.get('{}/validate/venue?token={}'.format(API_URL, token), headers={'origin': 'http://localhost:3000'})

    # Then
    assert r.status_code == 202
    db.session.refresh(venue)
    assert venue.isValidated


@clean_database
@pytest.mark.standalone
def test_validate_venue_with_no_validation_token_returns_status_code_400_and_token_in_error(app):
    # When
    r = req.get('{}/validate/venue'.format(API_URL), headers={'origin': 'http://localhost:3000'})

    # Then
    assert r.status_code == 400
    assert r.json()['token'] == ['Vous devez fournir un jeton de validation']


@clean_database
@pytest.mark.standalone
def test_validate_venue_with_non_existing_validation_token_returns_status_code_404_and_token_in_error(app):
    # When
    r = req.get('{}/validate/venue?token={}'.format(API_URL, '12345'), headers={'origin': 'http://localhost:3000'})

    # Then
    assert r.status_code == 404
    assert r.json()['token'] == ['Jeton inconnu']


@clean_database
@pytest.mark.standalone
def test_validate_user_when_validation_token_exists_should_put_validation_token_to_none_returns_status_code_202(app):
    # Given
    user = create_user()
    user.generate_validation_token()
    PcObject.check_and_save(user)

    # When
    response = req.get(API_URL + '/validate/user/' + user.validationToken, headers={'origin': 'http://localhost:3000'})

    # Then
    assert response.status_code == 202
    db.session.refresh(user)
    assert user.isValidated


@clean_database
@pytest.mark.standalone
def test_validate_user_when_validation_token_not_found_returns_status_code_404(app):
    # Given
    random_token = '0987TYGHHJMJ'

    # When
    response = req.get(API_URL + '/validate/user/' + random_token, headers={'origin': 'http://localhost:3000'})

    # Then
    assert response.status_code == 404
    assert response.json()['global'] == ['Ce lien est invalide']
