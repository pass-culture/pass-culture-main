from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_user,\
                             USER_TEST_ADMIN_EMAIL,\
                             USER_TEST_ADMIN_PASSWORD

def create_handmade_users():
    logger.info('create_handmade_users')

    users_by_name = {}

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

    users_by_name['jeune93 0'] = create_user(
        departement_code="93",
        email="pctest.jeune93.0@btmx.fr",
        first_name="PC Test Jeune",
        last_name="93 0",
        password="pctest.Jeune93.0",
        postal_code="93100",
        public_name="PC Test Jeune93 0"
    )

    users_by_name['jeune34 0'] = create_user(
        departement_code="34",
        email="pctest.jeune.34@btmx.fr",
        first_name="PC Test Jeune",
        last_name="34 0",
        password="pctest.Jeune34.0",
        postal_code="34080",
        public_name="PC Test Jeune34 0"
    )

    users_by_name['jeune97 0'] = create_user(
        departement_code="97",
        email="pctest.jeune97.0@btmx.fr",
        first_name="PC Test Jeune",
        last_name="97 0",
        password="pctest.Jeune97.0",
        postal_code="97351",
        public_name="PC Test Jeune97 0"
    )

    users_by_name['pro93 0'] = create_user(
        departement_code="93",
        email="pctest.pro93.0@btmx.fr",
        first_name="PC Test Pro",
        last_name="93 0",
        password="pctest.Pro93.0",
        postal_code="93100",
        public_name="PC Test Pro93 0"
    )

    users_by_name['pro93 1'] = create_user(
        departement_code="93",
        first_name="PC Test Pro",
        last_name="93 1",
        email="pctest.pro93.1@btmx.fr",
        password="pctest.Pro93.1",
        postal_code="93100",
        public_name="PC Test Pro93 1"
    )

    users_by_name['pro97 0'] = create_user(
        departement_code="97",
        first_name="PC Test Pro",
        last_name="97 0",
        email="pctest.pro97.0@btmx.fr",
        password="pctest.Pro97.0",
        postal_code="97351",
        public_name="PC Test Pro97 0"
    )

    PcObject.check_and_save(*users_by_name.values())

    logger.info('created {} users'.format(len(users_by_name)))

    return users_by_name
