from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_deposit

def create_scratch_deposits(users_by_name):
    logger.info('create_scratch_deposits')

    deposits_by_name = {}

    deposits_by_name['jeune 93 / public / 500'] = create_deposit(
        users_by_name['jeune 93'],
        None,
        amount=500
    )

    PcObject.check_and_save(*deposits_by_name.values())

    return deposits_by_name
