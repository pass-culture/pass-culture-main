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
from models.event_occurrence import EventOccurrence
from models.mediation import Mediation
from models.stock import Stock
from models.offerer import Offerer
from models.venue_provider import VenueProvider
from models.local_provider_event import LocalProviderEvent
from models.local_provider import LocalProvider
from models.offer import Offer
from models.provider import Provider
from models.recommendation import Recommendation
from models.thing import Thing
from models.user_offerer import UserOfferer
from models.user import User
from models.venue import Venue

# -*- coding: utf-8 -*-
from flask import current_app as app
from pprint import pprint

from utils.test_utils import API_URL, req, req_with_auth

@app.manager.command
def get(url, authenticated=False):
    if authenticated:
        r = req_with_auth.get(API_URL+url)
    else:
        r = req.get(API_URL+url)
    if r.headers.get('content-type') == 'application/json':
        pprint(r.json())
    else:
        print(r.text)
