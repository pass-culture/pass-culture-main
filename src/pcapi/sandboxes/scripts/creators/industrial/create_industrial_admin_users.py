from datetime import datetime, timedelta

from pcapi.repository import repository
from pcapi.model_creators.generic_creators import create_user
from pcapi.utils.logger import logger

ADMINS_COUNT = 1
departement_codes = ["93", "97"]


def create_industrial_admin_users():
    logger.info('create_industrial_admin_users')

    users_by_name = {}

    for departement_code in departement_codes:

        for admin_count in range(ADMINS_COUNT):
            email = "pctest.admin{}.{}@btmx.fr".format(departement_code, admin_count)
            users_by_name['admin{} {}'.format(departement_code, admin_count)] = create_user(
                reset_password_token_validity_limit=datetime.utcnow() + timedelta(hours=24),
                can_book_free_offers=False,
                date_of_birth=None,
                departement_code=str(departement_code),
                email=email,
                first_name="PC Test Admin",
                is_admin=True,
                last_name="{} {}".format(departement_code, admin_count),
                postal_code="{}100".format(departement_code),
                public_name="PC Test Admin {} {}".format(departement_code, admin_count))

    repository.save(*users_by_name.values())

    logger.info('created {} users'.format(len(users_by_name)))

    return users_by_name
