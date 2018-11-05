from models import UserOfferer
from models.pc_object import PcObject
from utils.logger import logger

def create_or_find_user_offerer(user_offerer_mock, user=None, offerer=None, store=None):
    if user is None:
        user = store['users_by_key'][user_offerer_mock['userKey']]
    if offerer is None:
        offerer = store['offerers_by_key'][user_offerer_mock['offererKey']]

    user_offerer = UserOfferer.query.filter_by(
        userId=user.id,
        offererId=offerer.id
    ).first()

    if query.count() == 0:
        user_offerer = UserOfferer(from_dict=user_offerer_mock)
        user_offerer.offerer = offerer
        user_offerer.user = user
        PcObject.check_and_save(user_offerer)
        logger.info("created user_offerer"  + str(user_offerer))
    else:
        logger.info('--aleady here-- user_offerer' + str(user_offerer))

    return user_offerer

def create_or_find_user_offerers(*user_offerer_mocks, store=None):
    if store is None:
        store = {}

    user_offerers_count = str(len(user_offerer_mocks))
    logger.info("user_offerer mocks " + user_offerers_count)

    store['user_offerers_by_key'] = {}

    for (user_offerer_index, user_offerer_mock) in enumerate(user_offerer_mocks):
        logger.info("look user_offerer " + store['users_by_key'][user_offerer_mock['userKey']].email + " " + store['offerers_by_key'][user_offerer_mock['offererKey']].name + str(user_offerer_index) + "/" + user_offerers_count)
        user_offerer = create_or_find_user_offerer(user_offerer_mock, store=store)
        store['user_offerers_by_key'][user_offerer_mock['key']] = user_offerer
