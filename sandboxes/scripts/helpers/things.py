from models import Thing
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_thing(thing_mock):
    thing = Thing.query.filter_by(name=thing_mock['name']).first()

    logger.info("look thing " + thing_mock['name'] + " " + thing_mock.get('id'))

    if thing is None:
        thing = Thing(from_dict=thing_mock)
        if 'id' in thing_mock:
            thing.id = dehumanize(thing_mock['id'])
        PcObject.check_and_save(thing)
        logger.info("created thing " + str(thing))
    else:
        logger.info('--already here-- thing ' + str(thing))

    return thing

def create_or_find_things(*thing_mocks):
    things_count = str(len(thing_mocks))
    logger.info("thing mocks " + things_count)

    things = []
    for (thing_index, thing_mock) in enumerate(thing_mocks):
        logger.info(str(thing_index) + "/" + things_count)
        thing = create_or_find_thing(thing_mock)
        things.append(thing)

    return things
