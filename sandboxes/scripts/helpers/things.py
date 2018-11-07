from models import Thing
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_thing(thing_mock):
    logger.info("look thing " + thing_mock['name'] + " " + thing_mock.get('id'))

    if 'id' in thing_mock:
        thing = Thing.query.get(dehumanize(thing_mock['id']))
    else:
        thing = Thing.query.filter_by(name=thing_mock['name']).first()

    if thing is None:
        thing = Thing(from_dict=thing_mock)
        if 'id' in thing_mock:
            thing.id = dehumanize(thing_mock['id'])
        PcObject.check_and_save(thing)
        logger.info("created thing " + str(thing))
    else:
        logger.info('--already here-- thing ' + str(thing))

    return thing
