from models.versioned_mixin import VersionedMixin
from models.api_errors import ApiErrors
from models.pc_object import PcObject
from models.deactivable_mixin import DeactivableMixin
from models.extra_data_mixin import ExtraDataMixin
from models.has_address_mixin import HasAddressMixin
from models.has_thumb_mixin import HasThumbMixin
from models.needs_validation_mixin import NeedsValidationMixin
from models.providable_mixin import ProvidableMixin
from models.booking import Booking
from models.event import Event
from models.event_occurence import EventOccurence
from models.mediation import Mediation
from models.offer import Offer
from models.offerer import Offerer
from models.venue_provider import VenueProvider
from models.local_provider_event import LocalProviderEvent
from models.local_provider import LocalProvider
from models.occasion import Occasion
from models.provider import Provider
from models.recommendation import Recommendation
from models.thing import Thing
from models.user_offerer import UserOfferer
from models.user import User
from models.venue import Venue

from utils.human_ids import dehumanize, humanize
from utils.test_utils import API_URL, req, req_with_auth


def test_10_get_occasions():
    r = req_with_auth().get(API_URL + '/occasions')
    assert r.status_code == 200
    occasions = r.json()
    assert len(occasions) == 10
    last_id = dehumanize(occasions[0]['id'])
    r = req_with_auth().get(API_URL + '/occasions?page=1')
    assert r.status_code == 200
    occasions = r.json()
    assert len(occasions) == 10
    assert dehumanize(occasions[0]['id']) == last_id
    r = req_with_auth().get(API_URL + '/occasions?page=2')
    assert r.status_code == 200
    occasions = r.json()
    assert dehumanize(occasions[0]['id']) == last_id-10
    r = req_with_auth().get(API_URL + '/occasions?venueId='+humanize(1))
    assert r.status_code == 200
    occasions = r.json()
    for occasion in occasions:
        assert occasion['venueId'] == humanize(1)
    r = req_with_auth().get(API_URL + '/occasions?venueId='+humanize(2))
    assert r.status_code == 200
    occasions = r.json()
    for occasion in occasions:
        assert occasion['venueId'] == humanize(2)
    r = req_with_auth().get(API_URL + '/occasions?venueId='+humanize(2)+'&page=2')
    assert r.status_code == 200
    occasions = r.json()
    for occasion in occasions:
        assert occasion['venueId'] == humanize(2)
    r = req_with_auth().get(API_URL + '/occasions?venueId='+humanize(2)+'&page=1&search=guide')
    assert r.status_code == 200
    occasions = r.json()
    assert len(occasions) == 10
    for occasion in occasions:
        assert occasion['venueId'] == humanize(2)
        assert 'guide' in occasion['thing']['name'].lower()
    r = req_with_auth().get(API_URL + '/occasions?venueId='+humanize(2)+'&page=2&search=guide')
    assert r.status_code == 200
    occasions = r.json()
    assert len(occasions) == 2
    for occasion in occasions:
        assert occasion['venueId'] == humanize(2)
        assert 'guide' in occasion['thing']['name'].lower()


def test_11_create_thing_occasion():
    data = {
            'venueId': humanize(3),
            'thingId': humanize(1)
           }
    r_create = req_with_auth().post(API_URL + '/occasions', json=data)
    assert r_create.status_code == 201


def test_12_create_event_occasion():
    data = {
            'venueId': humanize(3),
            'eventId': humanize(1)
           }
    r_create = req_with_auth().post(API_URL + '/occasions', json=data)
    assert r_create.status_code == 201
