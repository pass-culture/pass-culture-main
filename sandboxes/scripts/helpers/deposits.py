from models import Deposit
from models.pc_object import PcObject
from utils.logger import logger


def create_or_find_deposit(deposit_mock, store=None):
    if store is None:
        store = {}
    user = store['users_by_key'][deposit_mock['userKey']]
    query = Deposit.query.filter_by(userId=user.id)
    if query.count() == 0:
        deposit = Deposit(from_dict=deposit_mock)
        deposit.user = user
        PcObject.check_and_save(deposit)
        logger.info("created deposit " + str(deposit))
    else:
        deposit = query.first()
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
