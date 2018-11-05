from models import Offerer
from models.pc_object import PcObject
from utils.logger import logger

def create_or_find_offerer(offerer_mock):
    query = Offerer.query.filter_by(name=offerer_mock['name'])

    if query.count() == 0:
        offerer = Offerer(from_dict=offerer_mock)
        PcObject.check_and_save(offerer)
        logger.info("created offerer"  + str(offerer) + " " + offerer_mock['key'])
    else:
        offerer = query.first()
        logger.info('--aleady here-- offerer' + str(offerer))

    return offerer

def create_or_find_offerers(*offerer_mocks, store=None):
    if store is None:
        store = {}

    offerers_count = str(len(offerer_mocks))
    logger.info("offerer mocks " + offerers_count)

    store['offerers_by_key'] = {}

    for (offerer_index, offerer_mock) in enumerate(offerer_mocks):
        logger.info("look offerer " + offerer_mock['key'] + " " + str(offerer_index) + "/" + offerers_count)
        offerer = create_or_find_offerer(offerer_mock)
        store['offerers_by_key'][offerer_mock['key']] = offerer
