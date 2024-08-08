import logging

from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import User


logger = logging.getLogger(__name__)


ADMINS_COUNT = 1
departement_codes = ["93", "97"]


def create_data_admin_users() -> dict[str, User]:
    logger.info("create_data_admin_users")

    users_by_name = {}

    for departement_code in departement_codes:
        for admin_count in range(ADMINS_COUNT):
            email = "pctest.admin{}.{}_DATA@example.com".format(departement_code, admin_count)
            user = users_factories.AdminFactory(
                departementCode=str(departement_code),
                email=email,
                firstName="PC Test DATA Admin",
                lastName="{} {}".format(departement_code, admin_count),
                postalCode="{}100".format(departement_code),
            )
            users_factories.UserProNewNavStateFactory(user=user)

            users_by_name["admin{} {}".format(departement_code, admin_count)] = user

    logger.info("created %d users", len(users_by_name))

    return users_by_name
