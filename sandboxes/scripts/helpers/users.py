from models import User
from models.pc_object import PcObject
from sandboxes.utils import store_public_object_from_sandbox_assets
from utils.logger import logger

def create_or_find_user(user_mock):
    query = User.query.filter_by(email=user_mock['email'])

    if query.count() == 0:
        user = User(from_dict=user_mock)
        PcObject.check_and_save(user)
        logger.info("created user"  + str(user) + " " + user_mock['email'])
        if 'thumbName' in user_mock:
            store_public_object_from_sandbox_assets("thumbs", user, user_mock['thumbName'])
    else:
        user = query.first()
        logger.info('--aleady here-- user' + str(user))

    return user

def create_or_find_users(*user_mocks, store=None):
    if store is None:
        store = {}

    users_count = str(len(user_mocks))
    logger.info("user mocks " + users_count)

    store['users_by_key'] = {}

    for (user_index, user_mock) in enumerate(user_mocks):
        logger.info("look user " + user_mock['email'] + " " + str(user_index) + "/" + users_count)
        user = create_or_find_user(user_mock)
        store['users_by_key'][user_mock['key']] = user
