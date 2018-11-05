from models import Deposit
from models.pc_object import PcObject
from utils.logger import logger


def create_or_find_deposit(deposit_mock, user=None, store=None):
    if user is None:
        user = store['users_by_key'][deposit_mock['userKey']]

    deposit = Deposit.query.filter_by(userId=user.id).first()

    if deposit is None:
        deposit = Deposit(from_dict=deposit_mock)
        deposit.user = user
        PcObject.check_and_save(deposit)
        logger.info("created deposit " + str(deposit))
    else:
        logger.info('--already here-- deposit' + str(deposit))

    return deposit

def create_or_find_deposits(*deposit_mocks, store=None):
    if store is None:
        store = {}

    deposits_count = str(len(deposit_mocks))
    logger.info("deposit mocks " + deposits_count)

    store['deposits_by_key'] = {}

    for (deposit_index, deposit_mock) in enumerate(deposit_mocks):
        logger.info("look deposit " + store['users_by_key'][deposit_mock['userKey']].email + " " + str(deposit_index) + "/" + deposits_count)
        deposit = create_or_find_deposit(deposit_mock, store=store)
        store['deposits_by_key'][deposit_mock['key']] = deposit
