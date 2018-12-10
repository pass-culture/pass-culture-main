from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_user_offerer

def create_handmade_user_offerers(users_by_name, offerers_by_name):
    logger.info('create_handmade_user_offerers')

    user_offerers_by_name = {}

    #
    # 93 HVUO
    #

    user_offerers_by_name['pro93 has-validated-unregistered-offerer / LE GRAND REX PARIS'] = create_user_offerer(
        is_admin=True,
        offerer=offerers_by_name['LE GRAND REX PARIS'],
        user=users_by_name['pro93 has-validated-unregistered-offerer']
    )

    user_offerers_by_name['pro93 has-validated-unregistered-offerer / THEATRE DU SOLEIL'] = create_user_offerer(
        offerer=offerers_by_name['THEATRE DU SOLEIL'],
        user=users_by_name['pro93 has-validated-unregistered-offerer']
    )

    user_offerers_by_name['pro93 has-validated-unregistered-offerer / NOUVEAU THEATRE DE MONTREUIL'] = create_user_offerer(
        offerer=offerers_by_name['NOUVEAU THEATRE DE MONTREUIL'],
        user=users_by_name['pro93 has-validated-unregistered-offerer']
    )

    user_offerers_by_name['pro93 has-validated-unregistered-offerer / LA MARBRERIE'] = create_user_offerer(
        offerer=offerers_by_name['LA MARBRERIE'],
        user=users_by_name['pro93 has-validated-unregistered-offerer']
    )

    #
    # 93 HVRO
    #

    user_offerers_by_name['pro93 has-validated-registered-offerer / THEATRE DE L ODEON'] = create_user_offerer(
        offerer=offerers_by_name['LE GRAND REX PARIS'],
        user=users_by_name['pro93 has-validated-registered-offerer']
    )

    user_offerers_by_name['pro93 has-validated-registered-offerer / THEATRE DE L ODEON'] = create_user_offerer(
        offerer=offerers_by_name['THEATRE DE L ODEON'],
        user=users_by_name['pro93 has-validated-registered-offerer']
    )

    #
    # 97 HVUO
    #

    user_offerers_by_name['pro97 has-validated-unregistered-offerer / KWATA'] = create_user_offerer(
        offerer=offerers_by_name['KWATA'],
        user=users_by_name['pro97 has-validated-unregistered-offerer']
    )

    PcObject.check_and_save(*user_offerers_by_name.values())

    logger.info('created {} user_offerers'.format(len(user_offerers_by_name)))

    return user_offerers_by_name
