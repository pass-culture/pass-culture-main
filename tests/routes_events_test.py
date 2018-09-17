import pytest

from models import PcObject
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import req_with_auth, create_user, API_URL, create_venue, create_offerer


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
def test_post_event_throws_400_when_no_venue_with_that_id(app):
    # Given
    user = create_user(email='test@email.com', password='P@55w0rd')
    offerer = create_offerer()
    venue = create_venue(offerer)
    PcObject.check_and_save(user, venue)

    json = {'name': 'La pièce de théâtre', 'durationMinutes': 60, 'venueId': humanize(venue.id)}
    # When
    request = req_with_auth('test@email.com', 'P@55w0rd').post(API_URL + '/events', json=json)

    # Then
    print(request.json())
    assert request.status_code == 201
    assert request.json()['durationMinutes'] == 60
    assert request.json()['name'] == 'La pièce de théâtre'
