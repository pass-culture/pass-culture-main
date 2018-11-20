import pytest

from models import PcObject, EventType
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import req_with_auth, create_user, API_URL, create_venue, create_offerer, create_user_offerer


@clean_database
@pytest.mark.standalone
def test_post_event_throws_400_when_no_venue_id(app):
    # Given
    user = create_user(email='test@email.com', password='P@55w0rd')
    json = {'name': 'La pièce de théâtre', 'durationMinutes': 60}
    PcObject.check_and_save(user)

    # When
    request = req_with_auth('test@email.com', 'P@55w0rd').post(API_URL + '/events', json=json)

    # Then
    assert request.status_code == 400
    assert request.json()['venueId'] == ['Vous devez préciser un identifiant de lieu']


@clean_database
@pytest.mark.standalone
def test_post_event_throws_400_when_no_venue_with_that_id(app):
    # Given
    user = create_user(email='test@email.com', password='P@55w0rd')
    json = {'name': 'La pièce de théâtre', 'durationMinutes': 60, 'venueId': humanize(123)}
    PcObject.check_and_save(user)

    # When
    request = req_with_auth('test@email.com', 'P@55w0rd').post(API_URL + '/events', json=json)

    # Then
    assert request.status_code == 400
    assert request.json()['venueId'] == ['Aucun objet ne correspond à cet identifiant dans notre base de données']


@clean_database
@pytest.mark.standalone
def test_post_event_returns_201_when_creating_a_new_event(app):
    # Given
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    PcObject.check_and_save(user, venue)

    json = {
        'name': 'La pièce de théâtre',
        'durationMinutes': 60,
        'venueId': humanize(venue.id),
        'type': str(EventType.SPECTACLE_VIVANT)
    }

    # When
    request = req_with_auth('test@email.com', 'P@55w0rd').post(API_URL + '/events', json=json)

    # Then
    assert request.status_code == 201
    assert request.json()['durationMinutes'] == 60
    assert request.json()['name'] == 'La pièce de théâtre'
    assert request.json()['type'] == 'EventType.SPECTACLE_VIVANT'


@clean_database
@pytest.mark.standalone
def test_post_event_returns_403_when_creating_a_new_activation_event_as_an_offerer_editor(app):
    # Given
    user = create_user(email='test@email.com', password='P@55w0rd', is_admin=False)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer, is_admin=False)
    venue = create_venue(offerer)
    PcObject.check_and_save(user_offerer, venue)

    json = {
        'name': "Offre d'activation",
        'durationMinutes': 60,
        'venueId': humanize(venue.id),
        'type': str(EventType.ACTIVATION)
    }

    # When
    request = req_with_auth('test@email.com', 'P@55w0rd').post(API_URL + '/events', json=json)

    # Then
    assert request.status_code == 403
    assert request.json()['type'] == ["Seuls les administrateurs du pass Culture peuvent créer des offres d'activation"]


@clean_database
@pytest.mark.standalone
def test_post_event_returns_403_when_creating_a_new_activation_event_as_an_offerer_admin(app):
    # Given
    user = create_user(email='test@email.com', password='P@55w0rd', is_admin=False)
    offerer = create_offerer()
    user_offerer = create_user_offerer(user, offerer, is_admin=True)
    venue = create_venue(offerer)
    PcObject.check_and_save(user_offerer, venue)

    json = {
        'name': "Offre d'activation",
        'durationMinutes': 60,
        'venueId': humanize(venue.id),
        'type': str(EventType.ACTIVATION)
    }

    # When
    request = req_with_auth('test@email.com', 'P@55w0rd').post(API_URL + '/events', json=json)

    # Then
    assert request.status_code == 403
    assert request.json()['type'] == ["Seuls les administrateurs du pass Culture peuvent créer des offres d'activation"]


@clean_database
@pytest.mark.standalone
def test_post_event_returns_201_when_creating_a_new_activation_event_as_a_global_admin(app):
    # Given
    user = create_user(email='test@email.com', can_book_free_offers=False, password='P@55w0rd', is_admin=True)
    offerer = create_offerer()
    venue = create_venue(offerer)
    PcObject.check_and_save(user, venue)

    json = {
        'name': "Offre d'activation",
        'durationMinutes': 60,
        'venueId': humanize(venue.id),
        'type': str(EventType.ACTIVATION)
    }

    # When
    request = req_with_auth('test@email.com', 'P@55w0rd').post(API_URL + '/events', json=json)

    # Then
    assert request.status_code == 201
