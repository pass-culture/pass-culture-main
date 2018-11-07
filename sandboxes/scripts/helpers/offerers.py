from models import Offerer
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger


def create_or_find_offerer(offerer_mock):
    if 'id' in offerer_mock:
        offerer = Offerer.query.get(dehumanize(offerer_mock['id']))
    else:
        offerer = Offerer.query.filter_by(name=offerer_mock['name']).first()

    logger.info("look offerer " + offerer_mock['name'] + " " + offerer_mock.get('id'))

    if offerer is None:
        offerer = Offerer(from_dict=offerer_mock)
        if 'id' in offerer_mock:
            offerer.id = dehumanize(offerer_mock['id'])
        PcObject.check_and_save(offerer)
        logger.info("created offerer"  + str(offerer))
    else:
        logger.info('--aleady here-- offerer' + str(offerer))

    return offerer
