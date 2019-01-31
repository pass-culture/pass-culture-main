from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_user
from sandboxes.scripts.utils.user_tags import JEUNES_TAGS, PROS_TAGS

ADMINS_COUNT = 1
DEPARTMENT_CODES = ["93", "97"]

def create_industrial_users():
    logger.info('create_industrial_users')

    users_by_name = {}

    validation_prefix, validation_suffix = 'AZERTY', 123


    # create a special validation user with a real signup siren
    # (because the inscription/validation asks for Siren ApiEntreprise)
    validation_token = '{}{}'.format(validation_prefix, validation_suffix)
    departement_code = 93
    tag = 'real-validation'
    short_tag = "".join([chunk[0].upper() for chunk in tag.split('-')])
    users_by_name['pro{} {}'.format(departement_code, tag)] = create_user(
        departement_code=str(departement_code),
        email="pctest.pro{}.{}@btmx.fr".format(departement_code, tag),
        first_name="PC Test Pro {}",
        last_name="{} {}".format(departement_code, short_tag),
        password="pctest.Pro{}.{}".format(departement_code, tag),
        postal_code="{}100".format(departement_code),
        public_name="PC Test Pro {} {}".format(departement_code, short_tag),
        validation_token=validation_token
    )
    validation_suffix += 1

    # loop on department and tags
    for departement_code in DEPARTMENT_CODES:

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

            if tag == "has-signed-up":
                validation_token = '{}{}'.format(validation_prefix, validation_suffix)
                validation_suffix += 1
            else:
                validation_token = None

            users_by_name['pro{} {}'.format(departement_code, tag)] = create_user(
                departement_code=str(departement_code),
                email="pctest.pro{}.{}@btmx.fr".format(departement_code, tag),
                first_name="PC Test Pro",
                last_name="{} {}".format(departement_code, short_tag),
                password="pctest.Pro{}.{}".format(departement_code, tag),
                postal_code="{}100".format(departement_code),
                public_name="PC Test Pro {} {}".format(departement_code, short_tag),
                validation_token=validation_token
            )

        for tag in JEUNES_TAGS:
            short_tag = "".join([chunk[0].upper() for chunk in tag.split('-')])

            if tag == "has-signed-up":
                reset_password_token = '{}{}'.format(validation_prefix, validation_suffix)
                validation_suffix += 1
            else:
                reset_password_token = None

            users_by_name['jeune{} {}'.format(departement_code, tag)] = create_user(
                departement_code=str(departement_code),
                email="pctest.jeune{}.{}@btmx.fr".format(departement_code, tag),
                first_name="PC Test Jeune",
                last_name="{} {}".format(departement_code, short_tag),
                password="pctest.Jeune{}.{}".format(departement_code, tag),
                postal_code="{}100".format(departement_code),
                public_name="PC Test Jeune {} {}".format(departement_code, short_tag),
                reset_password_token=reset_password_token
            )

    PcObject.check_and_save(*users_by_name.values())

    logger.info('created {} users'.format(len(users_by_name)))

    return users_by_name
