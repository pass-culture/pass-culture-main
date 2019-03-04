from models.pc_object import PcObject
from sandboxes.scripts.utils.helpers import get_password_from_email
from tests.test_utils import create_user
from utils.logger import logger

ADMINS_COUNT = 1
departement_codeS = ["93", "97"]

def create_industrial_admin_users():
    logger.info('create_industrial_admin_users')

    users_by_name = {}

    # loop on department and tags
    for departement_code in departement_codeS:

        for admin_count in range(ADMINS_COUNT):
            email = "pctest.admin{}.{}@btmx.fr".format(departement_code, admin_count)
            users_by_name['admin{} {}'.format(departement_code, admin_count)] = create_user(
                public_name="PC Test Admin {} {}".format(departement_code, admin_count), first_name="PC Test Admin",
                last_name="{} {}".format(departement_code, admin_count), postal_code="{}100".format(departement_code),
                departement_code=str(departement_code), email=email, can_book_free_offers=False, is_admin=True)

    PcObject.check_and_save(*users_by_name.values())

    logger.info('created {} users'.format(len(users_by_name)))

    return users_by_name
