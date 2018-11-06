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

def create_or_find_offerers(*offerer_mocks):
    offerers_count = str(len(offerer_mocks))
    logger.info("offerer mocks " + offerers_count)

    offerers = []
    for (offerer_index, offerer_mock) in enumerate(offerer_mocks):
        logger.info(str(offerer_index) + "/" + offerers_count)
        offerer = create_or_find_offerer(offerer_mock)
        offerers.append(offerer)

    return offerers
