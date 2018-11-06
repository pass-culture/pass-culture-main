from models import User
from models.pc_object import PcObject
from sandboxes.utils import store_public_object_from_sandbox_assets
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_user(user_mock):
    user = User.query.filter_by(email=user_mock['email']).first()

    logger.info('look user ' + user_mock['email'])

    if user is None:
        user = User(from_dict=user_mock)
        if 'id' in user_mock:
            user.id = dehumanize(user_mock['id'])
        PcObject.check_and_save(user)
        logger.info("created user"  + str(user) + " " + user_mock['email'])
        if 'thumbName' in user_mock:
            store_public_object_from_sandbox_assets("thumbs", user, user_mock['thumbName'])
    else:
        logger.info('--aleady here-- user' + str(user))

    return user

def create_or_find_users(*user_mocks):
    users_count = str(len(user_mocks))
    logger.info("user mocks " + users_count)

    users = []
    for (user_index, user_mock) in enumerate(user_mocks):
        logger.info(str(user_index) + "/" + users_count)
        user = create_or_find_user(user_mock)
        users.append(user)

    return users
