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
from sqlalchemy import func, select

from utils.content import *
from utils.context import with_app_context
from utils.geoip import *
from utils.human_ids import *
from utils.includes import *
from utils.printer import *
from utils.token import *

app = Flask(__name__)

# necessary to have the query of model bound with the app context
with_app_context(app)

# add some cool local variables
locals().update(app.model)
session = app.db.session

client_user = User.query\
           .filter_by(email='arnaud.betremieux@beta.gouv.fr')\
           .first()
pro_user = User.query\
           .filter_by(email='erwan.ledoux@beta.gouv.fr')\
           .first()

def change_password(user, password):
    if type(user) != User:
        user = User.query.filter_by(email=user).one()
    user.setPassword(password)
    user = session.merge(user)
    PcObject.check_and_save(user)


# COOL CLI
#printify(listify(app.datascience.get_occasions(client_user, 2), offers_includes, cut=10))
