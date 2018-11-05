from models import Thing
from models.pc_object import PcObject
from utils.logger import logger

def create_or_find_thing(thing_mock):
    thing = Thing.query.filter_by(
        name=thing_mock['name']
    )

    if thing is None:
        thing = Thing(from_dict=thing_mock)
        PcObject.check_and_save(thing)
        logger.info("created thing " + str(thing) + " " + thing_mock['name'])
    else:
        logger.info('--already here-- thing' + str(thing))

    return thing

def create_or_find_things(*thing_mocks, store=None):
    if store is None:
        store = {}

    things_count = str(len(thing_mocks))
    logger.info("thing mocks " + things_count)

    store['things_by_key'] = {}

    for (thing_index, thing_mock) in enumerate(thing_mocks):
        logger.info("look thing " + thing_mock['name'] + " " + str(thing_index) + "/" + things_count)
        thing = create_or_find_thing(thing_mock)
        store['things_by_key'][thing_mock['key']] = thing
