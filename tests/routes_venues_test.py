import pytest
from flask import session

from models import PcObject, Venue
from models.db import db
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import API_URL, req_with_auth, create_venue, create_offerer, create_user, create_user_offerer


@clean_database
@pytest.mark.standalone
def test_modify_venue_returns_200_and_apply_modifications_on_venue(app):
    # given
    offerer = create_offerer()
    user = create_user(email='user.pro@test.com')
    venue = create_venue(offerer, name='L\'encre et la plume')
    user_offerer = create_user_offerer(user, offerer)
    PcObject.check_and_save(user_offerer, venue)
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    # when
    response = auth_request.patch(API_URL + '/venues/%s' % humanize(venue.id), json={'name': 'Ma librairie'})

    # then
    assert response.status_code == 200
    db.session.refresh(venue)
    assert venue.name == 'Ma librairie'


# TODO: check venue modification with missing items


@clean_database
@pytest.mark.standalone
def test_modify_venue_with_bad_siret_returns_bad_request_with_custom_error_message(app):
    # given
    offerer = create_offerer()
    user = create_user(email='user.pro@test.com')
    venue = create_venue(offerer, name='L\'encre et la plume')
    user_offerer = create_user_offerer(user, offerer)
    PcObject.check_and_save(user_offerer, venue)
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    # when
    response = auth_request.patch(API_URL + '/venues/%s' % humanize(venue.id), json={'siret': '999'})

    # then
    assert response.status_code == 400
    assert 'siret' in response.json()


@clean_database
@pytest.mark.standalone
def test_modify_venue_with_is_virtual_returns_400_if_a_virtual_venue_already_exist_for_an_offerer(app):
    # given
    offerer = create_offerer()
    user = create_user(email='user.pro@test.com')
    venue1 = create_venue(offerer, name='Les petits papiers', is_virtual=True, siret=None)
    venue2 = create_venue(offerer, name='L\'encre et la plume', is_virtual=False)
    user_offerer = create_user_offerer(user, offerer)
    PcObject.check_and_save(user_offerer, venue1, venue2)
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    # when
    response = auth_request.patch(API_URL + '/venues/%s' % humanize(venue2.id), json={'isVirtual': True})

    # then
    assert response.status_code == 400
    assert response.json() == {'isVirtual': ['Un lieu pour les offres numériques existe déjà pour cette structure']}


@clean_database
@pytest.mark.standalone
def test_modify_venue_with_is_virtual_returns_400_if_a_virtual_venue_already_exist_for_an_offerer(app):
    # given
    offerer = create_offerer()
    user = create_user(email='user.pro@test.com')
    venue = create_venue(offerer, name='Les petits papiers', is_virtual=False)
    user_offerer = create_user_offerer(user, offerer)
    PcObject.check_and_save(user_offerer, venue)
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)
    data = {'latitude': -98.82387, 'longitude': '112°3534'}

    # when
    response = auth_request.patch(API_URL + '/venues/%s' % humanize(venue.id), json=data)

    # then
    assert response.status_code == 400
    assert response.json()['latitude'] == ['La latitude doit être comprise entre -90.0 et +90.0']
    assert response.json()['longitude'] == ['Format incorrect']


@clean_database
@pytest.mark.standalone
def test_create_venue_returns_201_with_the_newly_created_venue(app):
    # given
    offerer = create_offerer(siren='302559178')
    user = create_user(email='user.pro@test.com')
    user_offerer = create_user_offerer(user, offerer)
    PcObject.check_and_save(user_offerer)
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)
    venue_data = {
        'name': 'Ma venue',
        'siret': '30255917810045',
        'address': '75 Rue Charles Fourier, 75013 Paris',
        'postalCode': '75200',
        'bookingEmail': 'toto@btmx.fr',
        'city': 'Paris',
        'managingOffererId': humanize(offerer.id),
        'latitude': 48.82387,
        'longitude': 2.35284
    }

    # when
    response = auth_request.post(API_URL + '/venues/', json=venue_data)

    # then
    assert response.status_code == 201
    id = response.json()['id']

    response_get = auth_request.get(API_URL + '/venues/' + id)

    assert response_get.status_code == 200
    created_venue_data = response_get.json()

    for (key, value) in venue_data.items():
        assert created_venue_data[key] == venue_data[key]

    # TODO: check thumb presence
    # TODO: check offerer linked to venue at creation


@clean_database
@pytest.mark.standalone
def test_create_venue_returns_400_if_a_virtual_venue_already_exist_for_an_offerer(app):
    # given
    offerer = create_offerer(siren='302559178')
    user = create_user(email='user.pro@test.com')
    user_offerer = create_user_offerer(user, offerer)
    venue = create_venue(offerer, name='L\'encre et la plume', is_virtual=True, siret=None)
    PcObject.check_and_save(venue, user_offerer)

    venue_data = {
        'name': 'Ma venue',
        'siret': '30255917810045',
        'address': '75 Rue Charles Fourier, 75013 Paris',
        'postalCode': '75200',
        'bookingEmail': 'toto@btmx.fr',
        'city': 'Paris',
        'managingOffererId': humanize(offerer.id),
        'latitude': 48.82387,
        'longitude': 2.35284,
        'isVirtual': True
    }

    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    # when
    response = auth_request.post(API_URL + '/venues/', json=venue_data)

    # then
    assert response.status_code == 400
    assert response.json() == {'isVirtual': ['Un lieu pour les offres numériques existe déjà pour cette structure']}


@clean_database
@pytest.mark.standalone
def test_create_venue_returns_400_if_given_latitude_and_longitudes_are_invalid(app):
    # given
    offerer = create_offerer(siren='302559178')
    user = create_user(email='user.pro@test.com')
    user_offerer = create_user_offerer(user, offerer)
    PcObject.check_and_save(user_offerer)

    data = {
        'name': 'Ma venue',
        'siret': '30255917810045',
        'address': '75 Rue Charles Fourier, 75013 Paris',
        'postalCode': '75200',
        'bookingEmail': 'toto@btmx.fr',
        'city': 'Paris',
        'managingOffererId': humanize(offerer.id),
        'latitude': -98.82387,
        'longitude': '112°3534',
        'isVirtual': False
    }

    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    # when
    response = auth_request.post(API_URL + '/venues/', json=data)

    # then
    assert response.status_code == 400
    assert response.json()['latitude'] == ['La latitude doit être comprise entre -90.0 et +90.0']
    assert response.json()['longitude'] == ['Format incorrect']


@clean_database
@pytest.mark.standalone
def test_get_venue_should_when_current_user_doesnt_have_rights_status_code_403(app):
    # given
    offerer = create_offerer()
    user = create_user(email='user.pro@test.com')
    venue = create_venue(offerer, name='L\'encre et la plume')
    PcObject.check_and_save(user, venue)
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    # when
    response = auth_request.get(API_URL + '/venues/%s' % humanize(venue.id))

    # then
    assert response.status_code == 403
    assert response.json()['global'] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]


@clean_database
@pytest.mark.standalone
def test_patch_venues_on_managing_offerer_id_returns_status_code_400_and_managing_offerer_id_in_error(app):
    # Given
    offerer = create_offerer(siren='123456789')
    other_offerer = create_offerer(siren='987654321')
    user = create_user(email='user.pro@test.com')
    venue = create_venue(offerer, name='Les petits papiers', is_virtual=False)
    user_offerer = create_user_offerer(user, offerer)
    PcObject.check_and_save(user_offerer, venue, other_offerer)
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    # When
    response = auth_request.patch(API_URL + '/venues/%s' % humanize(venue.id), json={'managingOffererId': humanize(other_offerer.id)})

    # Then
    assert response.status_code == 400
    assert response.json()['managingOffererId'] == ['Vous ne pouvez pas changer la structure d\'un lieu']


@clean_database
@pytest.mark.standalone
def test_patch_venues_on_siret_returns_status_code_400_and_siret_in_error(app):
    # Given
    offerer = create_offerer()
    user = create_user()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    siret = offerer.siren + '11111'
    venue = create_venue(offerer, siret=siret)
    PcObject.check_and_save(user_offerer, venue)
    venue_data = {
        'siret': offerer.siren + '12345',
    }
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    # when
    response = auth_request.patch(API_URL + '/venues/%s' % humanize(venue.id), json=venue_data)

    # Then
    assert response.status_code == 400
    assert response.json()['siret'] == ['Vous ne pouvez pas modifier le siret d\'un lieu']


@clean_database
@pytest.mark.standalone
def test_post_venues_without_siret_and_with_comment_returns_status_code_201_and_creates_not_validated_venue(app):
    # Given
    offerer = create_offerer()
    user = create_user()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    PcObject.check_and_save(user_offerer)
    venue_data = {
        'name': 'Ma venue',
        'comment': 'Je ne mets pas de SIRET pour une bonne raison',
        'address': '75 Rue Charles Fourier, 75013 Paris',
        'postalCode': '75200',
        'bookingEmail': 'toto@btmx.fr',
        'city': 'Paris',
        'managingOffererId': humanize(offerer.id),
        'latitude': 48.82387,
        'longitude': 2.35284
    }
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    # when
    response = auth_request.post(API_URL + '/venues/', json=venue_data)

    # Then
    assert response.status_code == 201
    venue = Venue.query.first()
    assert not venue.isValidated


@clean_database
@pytest.mark.standalone
def test_post_venues_with_siret_returns_status_code_201_and_creates_validated_venue(app):
    # Given
    offerer = create_offerer()
    user = create_user()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    PcObject.check_and_save(user_offerer)
    venue_data = {
        'name': 'Ma venue',
        'siret': offerer.siren + '12345',
        'address': '75 Rue Charles Fourier, 75013 Paris',
        'postalCode': '75200',
        'bookingEmail': 'toto@btmx.fr',
        'city': 'Paris',
        'managingOffererId': humanize(offerer.id),
        'latitude': 48.82387,
        'longitude': 2.35284
    }
    auth_request = req_with_auth(email=user.email, password=user.clearTextPassword)

    # when
    response = auth_request.post(API_URL + '/venues/', json=venue_data)

    # Then
    assert response.status_code == 201
    venue = Venue.query.first()
    assert venue.isValidated
