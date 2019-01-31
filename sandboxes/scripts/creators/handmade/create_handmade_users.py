from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_user,\
                             USER_TEST_ADMIN_EMAIL,\
                             USER_TEST_ADMIN_PASSWORD

def create_handmade_users():
    logger.info('create_handmade_users')

    users_by_name = {}

    ######################################
    # ADMINS
    ######################################

    users_by_name['admin93 0'] = create_user(
        can_book_free_offers=False,
        departement_code="93",
        email=USER_TEST_ADMIN_EMAIL,
        first_name="PC Test Admin",
        is_admin=True,
        last_name="93 0",
        password=USER_TEST_ADMIN_PASSWORD,
        postal_code="93100",
        public_name="PC Test Admin93 0"
    )

    ######################################
    # PRO
    ######################################

    users_by_name['pro93 has-signed-up'] = create_user(
        departement_code="93",
        first_name="PC Test Pro",
        last_name="93 HSU",
        email="pctest.pro93.has-signed-up@btmx.fr",
        password="pctest.Pro93.has-signed-up",
        postal_code="93100",
        public_name="PC Test Pro93 HSU",
        validation_token='AZERTY123'
    )

    users_by_name['pro93 has-validated-unregistered-offerer'] = create_user(
        departement_code="93",
        email="pctest.pro93.has-validated-unregistered-offerer@btmx.fr",
        first_name="PC Test Pro",
        last_name="93 HVUO",
        password="pctest.Pro93.has-validated-unregistered-offerer",
        postal_code="93100",
        public_name="PC Test Pro93 HVUO"
    )

    users_by_name['pro93 has-validated-registered-offerer'] = create_user(
        departement_code="93",
        first_name="PC Test Pro",
        last_name="93 HVRO",
        email="pctest.pro93.has-validated-registered-offerer@btmx.fr",
        password="pctest.Pro93.has-validated-registered-offerer",
        postal_code="93100",
        public_name="PC Test Pro93 HVRO"
    )

    users_by_name['pro97 has-validated-unregistered-offerer'] = create_user(
        departement_code="97",
        first_name="PC Test Pro",
        last_name="97 HVUO",
        email="pctest.pro97.has-validated-unregistered-offerer@btmx.fr",
        password="pctest.Pro97.has-validated-unregistered-offerer",
        postal_code="97351",
        public_name="PC Test Pro97 HVUO"
    )

    ######################################
    # JEUNES
    ######################################

    users_by_name['jeune93 has-signed-up'] = create_user(
        departement_code="93",
        email="pctest.jeune93.has-signed-up@btmx.fr",
        first_name="PC Test Jeune",
        last_name="93 HSU",
        password="pctest.Jeune93.has-signed-up",
        postal_code="93100",
        public_name="PC Test Jeune93 HSU",
        validation_token='AZERTY125'
    )

    users_by_name['jeune93 has-booked-some'] = create_user(
        departement_code="93",
        email="pctest.jeune93.has-booked-some@btmx.fr",
        first_name="PC Test Jeune",
        last_name="93 HBS",
        password="pctest.Jeune93.has-booked-some",
        postal_code="93100",
        public_name="PC Test Jeune93 HBS"
    )

    users_by_name['jeune34 0'] = create_user(
        departement_code="34",
        email="pctest.jeune34.has-signed-up@btmx.fr",
        first_name="PC Test Jeune",
        last_name="34 has-signed-up",
        password="pctest.Jeune34.has-signed-up",
        postal_code="34080",
        public_name="PC Test Jeune34 HSU",
        validation_token='AZERTY126'
    )

    users_by_name['jeune97 has-booked-some'] = create_user(
        departement_code="97",
        email="pctest.jeune97.has-booked-some@btmx.fr",
        first_name="PC Test Jeune",
        last_name="97 HBS",
        password="pctest.Jeune97.has-booked-some",
        postal_code="97351",
        public_name="PC Test Jeune97 HBS"
    )

    PcObject.check_and_save(*users_by_name.values())

    logger.info('created {} users'.format(len(users_by_name)))

    return users_by_name
