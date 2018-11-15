from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_user

ADMINS_COUNT = 2
JEUNES_COUNT = 2
PROS_COUNT = 2
DEPARTEMENT_CODES = ["93", "97"]

def create_industrial_users():
    logger.info('create_industrial_users')

    users_by_name = {}

    for departement_code in DEPARTEMENT_CODES:

        for admin_count in range(ADMINS_COUNT):
            users_by_name['admin {} {}'.format(departement_code, admin_count)] = create_user(
                can_book_free_offers=False,
                departement_code=str(departement_code),
                email="pctest.admin{}.{}@btmx.fr".format(departement_code, admin_count),
                first_name="PC Test Admin",
                is_admin=True,
                last_name="{} {}".format(departement_code, admin_count),
                password="pctest.Admin{}.{}".format(departement_code, admin_count),
                postal_code="{}100".format(departement_code),
                public_name="PC Test Admin {} {}".format(departement_code, admin_count)
            )

        for pro_count in range(PROS_COUNT):
            users_by_name['pro {} {}'.format(departement_code, pro_count)] = create_user(
                departement_code=str(departement_code),
                email="pctest.pro{}.{}@btmx.fr".format(departement_code, pro_count),
                first_name="PC Test Pro",
                last_name="{} {}".format(departement_code, pro_count),
                password="pctest.Pro{}.{}".format(departement_code, pro_count),
                postal_code="{}100".format(departement_code),
                public_name="PC Test Pro {} {}".format(departement_code, pro_count)
            )

        for jeune_count in range(JEUNES_COUNT):
            users_by_name['jeune {} {}'.format(departement_code, jeune_count)] = create_user(
                departement_code=str(departement_code),
                email="pctest.jeune{}.{}@btmx.fr".format(departement_code, jeune_count),
                first_name="PC Test Jeune",
                last_name="{} {}".format(departement_code, jeune_count),
                password="pctest.Jeune{}.{}".format(departement_code, jeune_count),
                postal_code="{}100".format(departement_code),
                public_name="PC Test Jeune {} {}".format(departement_code, jeune_count)
            )

    PcObject.check_and_save(*users_by_name.values())

    return users_by_name
