from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_user_offerer

def create_handmade_user_offerers(users_by_name, offerers_by_name):
    logger.info('create_handmade_user_offerers')

    user_offerers_by_name = {}

    user_offerers_by_name['pro 1 / LE GRAND REX PARIS'] = create_user_offerer(
        is_admin=True,
        offerer=offerers_by_name['LE GRAND REX PARIS'],
        user=users_by_name['pro 1']
    )
    user_offerers_by_name['pro 1 / THEATRE DE L ODEON'] = create_user_offerer(
        offerer=offerers_by_name['THEATRE DE L ODEON'],
        user=users_by_name['pro 1']
    )
    user_offerers_by_name['pro 1 / THEATRE DU SOLEIL'] = create_user_offerer(
        offerer=offerers_by_name['THEATRE DU SOLEIL'],
        user=users_by_name['pro 1']
    )

    PcObject.check_and_save(*user_offerers_by_name.values())

    return user_offerers_by_name
