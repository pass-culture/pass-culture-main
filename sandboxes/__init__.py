
""" sandbox """
import json
from pprint import pprint
import sys

from models.pc_object import PcObject
from sandboxes.scripts.helpers import create_or_find_bookings,\
                                      create_or_find_deposits,\
                                      create_or_find_event_occurrences,\
                                      create_or_find_events,\
                                      create_or_find_mediations,\
                                      create_or_find_offerers,\
                                      create_or_find_offers,\
                                      create_or_find_recommendations,\
                                      create_or_find_stocks,\
                                      create_or_find_things,\
                                      create_or_find_user_offerers,\
                                      create_or_find_users,\
                                      create_or_find_venues
from sandboxes.scripts.mocks import *
from sandboxes.scripts import sandbox_light, sandbox_webapp
from sandboxes.utils import store_public_object_from_sandbox_assets
from utils.logger import logger

def save_sandbox_in_db(name):
    function_name = "sandboxes.scripts.sandbox_" + name
    sandbox_module = sys.modules[function_name]
    create_or_find_offerers(*sandbox_module.OFFERER_MOCKS)
    create_or_find_users(*sandbox_module.USER_MOCKS)
    create_or_find_user_offerers(*sandbox_module.USER_OFFERER_MOCKS)
    create_or_find_venues(*sandbox_module.VENUE_MOCKS)
    create_or_find_events(*sandbox_module.EVENT_MOCKS)
    create_or_find_things(*sandbox_module.THING_MOCKS)
    create_or_find_offers(*sandbox_module.OFFER_MOCKS)
    create_or_find_event_occurrences(*sandbox_module.EVENT_OCCURRENCE_MOCKS)
    create_or_find_stocks(*sandbox_module.STOCK_MOCKS)
    create_or_find_deposits(*sandbox_module.DEPOSIT_MOCKS)
    create_or_find_mediations(*sandbox_module.MEDIATION_MOCKS)
    create_or_find_recommendations(*sandbox_module.RECOMMENDATION_MOCKS)
    create_or_find_bookings(*sandbox_module.BOOKING_MOCKS)
