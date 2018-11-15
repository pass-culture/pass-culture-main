from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_user,\
                             USER_TEST_ADMIN_EMAIL,\
                             USER_TEST_ADMIN_PASSWORD

def create_handmade_users():
    logger.info('create_handmade_users')

    users_by_name = {}

    users_by_name['admin 1'] = create_user(
        can_book_free_offers=False,
        departement_code="93",
        email=USER_TEST_ADMIN_EMAIL,
        first_name="PC Test",
        is_admin=True,
        last_name="Admin 1",
        password=USER_TEST_ADMIN_PASSWORD,
        postal_code="93100",
        public_name="PC Test Admin 1"
    )

    users_by_name['jeune 93'] = create_user(
        departement_code="93",
        email="pctest.jeune.93@btmx.fr",
        first_name="PC Test",
        last_name="Jeune 93",
        password="pctest.Jeune.93",
        postal_code="93100",
        public_name="PC Test Jeune 93"
    )

    users_by_name['jeune 34'] = create_user(
        departement_code="34",
        email="pctest.jeune.34@btmx.fr",
        first_name="PC Test",
        last_name="Jeune 34",
        password="pctest.Jeune.34",
        postal_code="34080",
        public_name="PC Test Jeune 34"
    )

    users_by_name['jeune 97'] = create_user(
        departement_code="97",
        email="pctest.jeune.97@btmx.fr",
        first_name="PC Test",
        last_name="Jeune 97",
        password="pctest.Jeune.97",
        postal_code="97351",
        public_name="PC Test Jeune 97"
    )

    users_by_name['pro 1'] = create_user(
        departement_code="93",
        email="pctest.pro.1@btmx.fr",
        first_name="PC Test",
        last_name="Pro 1",
        password="pctest.Pro.1",
        postal_code="93100",
        public_name="PC Test Pro 1"
    )

    users_by_name['pro 2'] = create_user(
        departement_code="93",
        first_name="PC Test",
        last_name="Pro 2",
        email="pctest.pro.2@btmx.fr",
        password="pctest.Pro.2",
        postal_code="93100",
        public_name="PC Test Pro 2"
    )

    users_by_name['pro 3'] = create_user(
        departement_code="97",
        first_name="PC Test",
        last_name="Pro 3",
        email="pctest.pro.3@btmx.fr",
        password="pctest.Pro.3",
        postal_code="97351",
        public_name="PC Test Pro 3"
    )

    PcObject.check_and_save(*users_by_name.values())

    return users_by_name
