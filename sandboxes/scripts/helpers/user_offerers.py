from models import Offerer, User, UserOfferer
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_user_offerer(user_offerer_mock):
    user = User.query.get(dehumanize(user_offerer_mock['userId']))
    offerer = Offerer.query.get(dehumanize(user_offerer_mock['offererId']))

    logger.info("create or find user_offerer " + user.email + " " + offerer.name + " " + user_offerer_mock.get('id'))

    user_offerer = UserOfferer.query.filter_by(
        userId=user.id,
        offererId=offerer.id
    ).first()

    if user_offerer is None:
        user_offerer = UserOfferer(from_dict=user_offerer_mock)
        user_offerer.offerer = offerer
        user_offerer.user = user
        if 'id' in user_offerer_mock:
            user_offerer.id = dehumanize(user_offerer_mock['id'])
        PcObject.check_and_save(user_offerer)
        logger.info("created user_offerer" + str(user_offerer))
    else:
        logger.info('--aleady here-- user_offerer' + str(user_offerer))

    return user_offerer
