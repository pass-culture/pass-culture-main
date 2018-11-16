from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_deposit

def create_industrial_deposits(users_by_name):
    logger.info('create_industrial_deposits')

    deposits_by_name = {}

    for (user_name, user) in users_by_name.items():

        if user.firstName != "PC Test Jeune":
            continue

        deposits_by_name['{} / public / 500'.format(user_name)] = create_deposit(
            user,
            None,
            amount=500
        )

    PcObject.check_and_save(*deposits_by_name.values())

    logger.info('created {} deposits'.format(len(deposits_by_name)))

    return deposits_by_name
