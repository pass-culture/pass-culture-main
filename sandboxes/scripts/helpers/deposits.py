from models import Deposit, User
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger


def create_or_find_deposit(deposit_mock, user=None):
    if user is None:
        user = User.query.get(dehumanize(deposit_mock['userId']))

    logger.info("look deposit " + user.email + " " + deposit_mock.get('id'))

    deposit = Deposit.query.filter_by(userId=user.id).first()

    if deposit is None:
        deposit = Deposit(from_dict=deposit_mock)
        deposit.user = user
        if 'id' in deposit_mock:
            deposit.id = dehumanize(deposit_mock['id'])
        PcObject.check_and_save(deposit)
        logger.info("created deposit " + str(deposit))
    else:
        logger.info('--already here-- deposit' + str(deposit))

    return deposit

def create_or_find_deposits(*deposit_mocks):
    deposits_count = str(len(deposit_mocks))
    logger.info("deposit mocks " + deposits_count)

    deposits = []
    for (deposit_index, deposit_mock) in enumerate(deposit_mocks):
        logger.info(str(deposit_index) + "/" + deposits_count)
        deposit = create_or_find_deposit(deposit_mock)
        deposits.append(deposit)

    return deposits
