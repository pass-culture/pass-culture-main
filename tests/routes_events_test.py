import pytest

from models import PcObject
from tests.conftest import clean_database
from utils.test_utils import req_with_auth, create_user, API_URL


@clean_database
@pytest.mark.standalone
def test_post_event_throws_400_when_no_venue_id(app):
    # Given
    user = create_user(email='test@email.com', password='P@55w0rd')
    json = {'name': 'La pièce de théâtre', 'durationMinutes': 60}
    PcObject.check_and_save(user)

    # When
    request = req_with_auth('test@email.com', 'P@55w0rd').post(API_URL + '/events', data=json)

    # Then
    assert request.status_code == 400
    print(vars(request))
    assert {'venueId': 'le lieu est invalide'} in request.json()