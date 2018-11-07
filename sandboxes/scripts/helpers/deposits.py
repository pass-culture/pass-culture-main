from models import Deposit, User
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger


def create_or_find_deposit(deposit_mock):
    user = User.query.get(dehumanize(deposit_mock['userId']))

    logger.info("look deposit " + user.email + " " + deposit_mock.get('id'))

    if 'id' in deposit_mock:
        deposit = Deposit.query.get(dehumanize(deposit_mock['id']))
    else:
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
