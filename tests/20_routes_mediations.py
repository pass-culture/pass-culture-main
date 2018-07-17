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

from flask import Flask
from flask_script import Manager
from os import path
from pathlib import Path
from time import sleep

from utils.human_ids import humanize
from utils.test_utils import API_URL, req_with_auth


def test_10_create_mediation():
    with open(Path(path.dirname(path.realpath(__file__))) / '..'
              / 'mock' / 'thumbs' / 'mediations' / '1', 'rb') as thumb_file:
        data = {
                'eventId': 'AE',
                'offererId': 'AE',
               }
        files = {
                 'thumb': ('1.jpg', thumb_file)
                }
        r_create = req_with_auth().post(API_URL + '/mediations',
                                        data=data,
                                        files=files)
        assert r_create.status_code == 201


#TODO
#def test_12_delete_mediation():
#    r_delete = req_with_auth().delete(API_URL + '/mediations/AE')
#    assert r_delete.status_code == 200
#    r_check = req_with_auth().get(API_URL + '/mediations/AE')
#    assert r_check.status_code == 404
