from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_user_offerer

def create_scratch_user_offerers(users_by_name, offerers_by_name):
    logger.info('create_scratch_user_offerers')

    user_offerers_by_name = {}

    user_offerers_by_name['pro_1_le_grand_rex_paris'] = create_user_offerer(
        is_admin=True,
        offerer=offerers_by_name['le_grand_rex_paris'],
        user=users_by_name['pro_1']
    )
    user_offerers_by_name['pro_1_le_grand_rex_paris'] = create_user_offerer(
        offerer=offerers_by_name['theatre_de_l_odeon'],
        user=users_by_name['pro_1']
    )
    user_offerers_by_name['pro_1_theatre_du_soleil'] = create_user_offerer(
        offerer=offerers_by_name['theatre_du_soleil'],
        user=users_by_name['pro_1']
    )

    PcObject.check_and_save(*user_offerers_by_name.values())

    return user_offerers_by_name
