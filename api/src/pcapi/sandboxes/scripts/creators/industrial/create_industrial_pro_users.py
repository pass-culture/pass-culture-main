import logging

from pcapi.core.offers.factories import UserOffererFactory
from pcapi.core.users import factories as users_factories
from pcapi.repository import repository


logger = logging.getLogger(__name__)


PROS_COUNT = 1
departement_codes = ["93", "97"]


def create_industrial_pro_users(offerers_by_name: dict) -> dict:
    logger.info("create_industrial_pro_users")

    users_by_name = {}

    offerers = list(offerers_by_name.values())

    for index, departement_code in enumerate(departement_codes):

        for pro_count in range(PROS_COUNT):
            email = "pctest.pro{}.{}@example.com".format(departement_code, pro_count)
            user = users_factories.ProFactory(
                dateOfBirth=None,
                departementCode=str(departement_code),
                email=email,
                firstName="PC Test Pro",
                lastName="{} {}".format(departement_code, pro_count),
                postalCode="{}100".format(departement_code),
                publicName="PC Test Pro {} {}".format(departement_code, pro_count),
            )
            users_by_name["pro{} {}".format(departement_code, pro_count)] = user
            UserOffererFactory(offerer=offerers[index], user=user)

    repository.save(*users_by_name.values())

    logger.info("created %d users", len(users_by_name))

    return users_by_name
