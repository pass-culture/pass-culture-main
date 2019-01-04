import secrets

import pytest

from models import Offerer, PcObject
from models.db import db
from tests.conftest import clean_database
from tests.files.transactions import VALID_TRANSACTION, INVALID_TRANSACTION, \
    VALID_TRANSACTION_WITH_MALFORMED_XML_DECLARATION
from utils.test_utils import req, create_user, req_with_auth, API_URL, create_offerer, create_user_offerer, \
    create_venue, create_payment_transaction


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
    assert response.json() == {}
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


@pytest.mark.standalone
class CertifyTransactionFileAuthenticityTest:
    @clean_database
    def test_returns_no_content_if_file_authenticity_is_certified(self, app):
        # given
        user = create_user(password='p@55sw0rd', is_admin=True, can_book_free_offers=False)
        transaction = create_payment_transaction(
            transaction_message_id='passCulture-SCT-20181015-114356',
            checksum='86055b286afd11316cd7cacd00e61034fddedda50c234c0157a8f0da6e30931e'
        )
        PcObject.check_and_save(user, transaction)

        auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

        # when
        response = auth_request.post(
            API_URL + '/validate/transaction/',
            data={},
            files={'file': ('transaction.xml', VALID_TRANSACTION)}
        )

        # then
        assert response.status_code == 204

    @clean_database
    def test_returns_bad_request_if_file_checksum_does_not_match_known_checksum(self, app):
        # given
        user = create_user(password='p@55sw0rd', is_admin=True, can_book_free_offers=False)
        transaction = create_payment_transaction(
            transaction_message_id='passCulture-SCT-20181015-114356',
            checksum='FAKE_CHECKSUM'
        )
        PcObject.check_and_save(user, transaction)

        auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

        # when
        response = auth_request.post(
            API_URL + '/validate/transaction/',
            data={},
            files={'file': ('transaction.xml', VALID_TRANSACTION)}
        )

        # then
        assert response.status_code == 400
        assert response.json()['xml'] == [
            "L'intégrité du document n'est pas validée"
        ]

    @clean_database
    def test_returns_unauthorized_if_user_is_not_logged_in(self, app):
        # when
        response = req.post(
            API_URL + '/validate/transaction/',
            data={},
            files={'file': ('transaction.xml', VALID_TRANSACTION)},
            headers={'origin': 'http://localhost:3000'}
        )

        # then
        assert response.status_code == 401

    @clean_database
    def test_returns_forbidden_if_current_user_is_not_admin(self, app):
        # given
        user = create_user(password='p@55sw0rd', is_admin=False, can_book_free_offers=True)
        transaction = create_payment_transaction(
            transaction_message_id='passCulture-SCT-20181015-114356',
            checksum='86055b286afd11316cd7cacd00e61034fddedda50c234c0157a8f0da6e30931e'
        )
        PcObject.check_and_save(user, transaction)

        auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

        # when
        response = auth_request.post(
            API_URL + '/validate/transaction/',
            data={},
            files={'file': ('transaction.xml', VALID_TRANSACTION)}
        )

        # then
        assert response.status_code == 403

    @clean_database
    def test_returns_not_found_if_message_id_from_file_is_unknown(self, app):
        # given
        user = create_user(password='p@55sw0rd', is_admin=True, can_book_free_offers=False)
        PcObject.check_and_save(user)

        auth_request = req_with_auth(email=user.email, password='p@55sw0rd')

        # when
        response = auth_request.post(
            API_URL + '/validate/transaction/',
            data={},
            files={'file': ('transaction.xml', VALID_TRANSACTION)}
        )

        # then
        assert response.status_code == 404
        assert response.json()['xml'] == [
            "L'identifiant du document XML 'MsgId' est inconnu"
        ]
