import secrets

import pytest

from models import Offerer
from tests.conftest import clean_database
from utils.test_utils import req, create_user, req_with_auth, API_URL, create_offerer


@clean_database
@pytest.mark.standalone
def test_should_not_be_able_to_validate_offerer_with_wrong_token(app):
    user = create_user(email='toto@btmx.fr', public_name='Toto', departement_code='93', password='toto12345678')
    PcObject.check_and_save(user)
    user.validationToken = secrets.token_urlsafe(20)
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
    PcObject.check_and_save(offerer)
    offerer_id = offerer.id
    del (offerer)

    token = Offerer.query \
        .filter_by(id=offerer_id) \
        .first().validationToken

    # When
    r = req.get(API_URL + '/validate?modelNames=Offerer&token=' + token)

    # Then
    assert r.status_code == 202
    offerer = Offerer.query \
        .filter_by(id=offerer_id) \
        .first()
    assert offerer.isValidated

# def test_14_get_profile_should_not_work_if_account_is_not_validated():
#    r = req_with_auth(email='toto@btmx.fr',
#                      password='toto12345678')\
#                    .get(API_URL + '/users/current')
#    assert r.status_code == 401
#    assert 'pas validé' in r.json()['identifier']


# def test_15_should_not_be_able_to_validate_user_with_wrong_token():
#    r = req_with_auth(email='toto@btmx.fr',
#                      password='toto12345678')\
#                 .get(API_URL + '/validate?modelNames=User&token=123')
#    assert r.status_code == 404


# def test_16_should_be_able_to_validate_user(app):
#    token = User.query\
#                .filter(User.validationToken != None)\
#                .first().validationToken
#    r = req_with_auth().get(API_URL + '/validate?modelNames=User&token='+token)
#    assert r.status_code == 202
