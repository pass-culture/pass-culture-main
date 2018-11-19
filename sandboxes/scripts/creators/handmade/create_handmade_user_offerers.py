from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_user_offerer

def create_handmade_user_offerers(users_by_name, offerers_by_name):
    logger.info('create_handmade_user_offerers')

    user_offerers_by_name = {}

    user_offerers_by_name['pro93 0 / LE GRAND REX PARIS'] = create_user_offerer(
        is_admin=True,
        offerer=offerers_by_name['LE GRAND REX PARIS'],
        user=users_by_name['pro93 0']
    )
    user_offerers_by_name['pro93 1 / THEATRE DE L ODEON'] = create_user_offerer(
        offerer=offerers_by_name['THEATRE DE L ODEON'],
        user=users_by_name['pro93 1']
    )
    user_offerers_by_name['pro93 0 / THEATRE DU SOLEIL'] = create_user_offerer(
        offerer=offerers_by_name['THEATRE DU SOLEIL'],
        user=users_by_name['pro93 0']
    )
    user_offerers_by_name['pro97 0 / KWATA'] = create_user_offerer(
        offerer=offerers_by_name['KWATA'],
        user=users_by_name['pro97 0']
    )

    PcObject.check_and_save(*user_offerers_by_name.values())

    logger.info('created {} user_offerers'.format(len(user_offerers_by_name)))

    return user_offerers_by_name
