from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_mediation

def create_scratch_mediations(offers_by_name):
    logger.info('create_scratch_mediations')

    mediations_by_name = {}

    mediations_by_name['e'] = create_mediation(offers_by_name['a'])

    PcObject.check_and_save(*mediations_by_name.values())

    return mediations_by_name
