from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_user

ADMINS_COUNT = 1
DEPARTEMENT_CODES = ["93", "97"]

PROS_TAGS = [
    "has-signed-up",
    "has-validated-email",
    "has-validated-unregistered-offerer",
    "has-validated-registered-offerer"
]

JEUNES_TAGS = [
    "has-signed-up",
    "has-booked-activation",
    "has-confirmed-activation",
    "has-booked-some",
    "has-no-more-money"
]

def create_industrial_users():
    logger.info('create_industrial_users')

    users_by_name = {}

    for departement_code in DEPARTEMENT_CODES:

        for admin_count in range(ADMINS_COUNT):
            users_by_name['admin{} {}'.format(departement_code, admin_count)] = create_user(
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

        for tag in PROS_TAGS:
            short_tag = "".join([chunk[0].upper() for chunk in tag.split('-')])
            users_by_name['pro{} {}'.format(departement_code, tag)] = create_user(
                departement_code=str(departement_code),
                email="pctest.pro{}.{}@btmx.fr".format(departement_code, tag),
                first_name="PC Test Pro",
                last_name="{} {}".format(departement_code, short_tag),
                password="pctest.Pro{}.{}".format(departement_code, tag),
                postal_code="{}100".format(departement_code),
                public_name="PC Test Pro {} {}".format(departement_code, short_tag)
            )

        for tag in JEUNES_TAGS:
            short_tag = "".join([chunk[0].upper() for chunk in tag.split('-')])
            users_by_name['jeune{} {}'.format(departement_code, tag)] = create_user(
                departement_code=str(departement_code),
                email="pctest.jeune{}.{}@btmx.fr".format(departement_code, tag),
                first_name="PC Test Jeune",
                last_name="{} {}".format(departement_code, short_tag),
                password="pctest.Jeune{}.{}".format(departement_code, tag),
                postal_code="{}100".format(departement_code),
                public_name="PC Test Jeune {} {}".format(departement_code, short_tag)
            )

    PcObject.check_and_save(*users_by_name.values())

    logger.info('created {} users'.format(len(users_by_name)))

    return users_by_name
