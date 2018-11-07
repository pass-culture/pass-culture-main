""" save sandbox """
import json
from pprint import pprint
import sys

from models.pc_object import PcObject
from sandboxes.scripts.helpers import create_or_find_booking,\
                                      create_or_find_deposit,\
                                      create_or_find_event_occurrence,\
                                      create_or_find_event,\
                                      create_or_find_mediation,\
                                      create_or_find_objects, \
                                      create_or_find_offerer,\
                                      create_or_find_offer,\
                                      create_or_find_recommendation,\
                                      create_or_find_stock,\
                                      create_or_find_thing,\
                                      create_or_find_user_offerer,\
                                      create_or_find_user,\
                                      create_or_find_venue
from sandboxes.scripts.mocks import *
from sandboxes.scripts import sandbox_light, sandbox_webapp
from utils.logger import logger

def save_sandbox(name):
    function_name = "sandboxes.scripts.sandbox_" + name
    sandbox_module = sys.modules[function_name]
    create_or_find_objects(
        *sandbox_module.OFFERER_MOCKS,
        create_or_find_object=create_or_find_offerer
    )
    create_or_find_objects(
        *sandbox_module.USER_MOCKS,
        create_or_find_object=create_or_find_user
    )
    create_or_find_objects(
        *sandbox_module.USER_OFFERER_MOCKS,
        create_or_find_object=create_or_find_user_offerer
    )
    create_or_find_objects(
        *sandbox_module.VENUE_MOCKS,
        create_or_find_object=create_or_find_venue
    )
    create_or_find_objects(
        *sandbox_module.EVENT_MOCKS,
        create_or_find_object=create_or_find_event
    )
    create_or_find_objects(
        *sandbox_module.THING_MOCKS,
        create_or_find_object=create_or_find_thing
    )
    create_or_find_objects(
        *sandbox_module.OFFER_MOCKS,
        create_or_find_object=create_or_find_offer
    )
    create_or_find_objects(
        *sandbox_module.EVENT_OCCURRENCE_MOCKS,
        create_or_find_object=create_or_find_event_occurrence
    )
    create_or_find_objects(
        *sandbox_module.STOCK_MOCKS,
        create_or_find_object=create_or_find_stock
    )
    create_or_find_objects(
        *sandbox_module.DEPOSIT_MOCKS,
        create_or_find_object=create_or_find_deposit
    )
    create_or_find_objects(
        *sandbox_module.MEDIATION_MOCKS,
        create_or_find_object=create_or_find_mediation
    )
    create_or_find_objects(
        *sandbox_module.RECOMMENDATION_MOCKS,
        create_or_find_object=create_or_find_recommendation
    )
    create_or_find_objects(
        *sandbox_module.BOOKING_MOCKS,
        create_or_find_object=create_or_find_booking
    )
