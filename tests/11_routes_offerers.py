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

from utils.test_utils import API_URL, req, req_with_auth


def test_10_get_offerers_should_work_only_when_logged_in():
    r = req.get(API_URL + '/offerers')
    assert r.status_code == 401


def test_10_get_offerers_should_return_a_list_of_offerers():
    r = req_with_auth().get(API_URL + '/offerers')
    assert r.status_code == 200
    offerers = r.json()
    assert len(offerers) == 11

#r = req.get(API_URL + '/offerers', headers={'apikey': ''})
