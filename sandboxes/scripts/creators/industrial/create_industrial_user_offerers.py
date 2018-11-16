from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_user_offerer

def create_industrial_user_offerers(users_by_name, offerers_by_name):
    logger.info('create_industrial_user_offerers')

    user_offerers_by_name = {}

    for (user_name, user) in users_by_name.items():

        for (offerer_name, offerer) in offerers_by_name.items():

            if offerer.postalCode[:2] != user.departementCode:
                continue

            user_offerers_by_name['{} / {}'.format(user_name, offerer_name)] = create_user_offerer(
                offerer=offerer,
                user=user
            )

    PcObject.check_and_save(*user_offerers_by_name.values())

    logger.info('created {} user_offerers'.format(len(user_offerers_by_name)))

    return user_offerers_by_name
