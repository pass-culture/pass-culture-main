import pytest

from models import PcObject
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import API_URL, req_with_auth, create_user, create_venue, \
    create_offerer, create_user_offerer


@clean_database
@pytest.mark.standalone
def test_unknown_properties_in_post_thing_can_be_found_later_in_get(app):
    # Given
    user = create_user(email='user@test.com', password='azerty123')
    offerer = create_offerer(siren='123456789')
    user_offerer = create_user_offerer(user, offerer)
    venue = create_venue(offerer)
    PcObject.check_and_save(offerer, user, user_offerer, venue)

    # when
    create_response = req_with_auth(email='user@test.com', password='azerty123')\
                        .post(API_URL + '/things',
                              json= { 'type': "ThingType.CINEMA",
                                      'name': "My thing",
                                      'description': "Ze thing that rocks",
                                      'durationMinutes': 122,
                                      'venueId': humanize(venue.id),
                                      'unknownProperty': "unknownPropertyValue" })
    assert create_response.status_code == 201
    event_id = create_response.json()['id']
    get_response = req_with_auth(email='user@test.com', password='azerty123')\
                     .get(API_URL + '/things/'+event_id)

    # then
    assert get_response.status_code == 200
    assert get_response.json()['unknownProperty'] == 'unknownPropertyValue'

