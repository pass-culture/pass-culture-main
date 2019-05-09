from models.pc_object import PcObject
from sandboxes.scripts.utils.helpers import get_password_from_email
from tests.test_utils import create_user
from utils.logger import logger

PROS_COUNT = 1
departement_codes = ["93", "97"]

def create_industrial_pro_users():
    logger.info('create_industrial_pro_users')

    users_by_name = {}

    # loop on department and tags
    for departement_code in departement_codes:

        for pro_count in range(PROS_COUNT):
            email = "pctest.pro{}.{}@btmx.fr".format(departement_code, pro_count)
            users_by_name['pro{} {}'.format(departement_code, pro_count)] = create_user(
                can_book_free_offers=False,
                departement_code=str(departement_code),
                email=email,
                first_name="PC Test Pro",
                is_admin=False,
                last_name="{} {}".format(departement_code, pro_count),
                password=get_password_from_email(email),
                postal_code="{}100".format(departement_code),
                public_name="PC Test Pro {} {}".format(departement_code, pro_count)
            )

    PcObject.check_and_save(*users_by_name.values())

    logger.info('created {} users'.format(len(users_by_name)))

    return users_by_name
