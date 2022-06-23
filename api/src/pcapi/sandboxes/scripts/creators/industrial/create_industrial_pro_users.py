import logging

from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import User
from pcapi.repository import repository
from pcapi.sandboxes.scripts.mocks.educational_siren_mocks import MOCK_ADAGE_ELIGIBLE_SIREN


logger = logging.getLogger(__name__)


PROS_COUNT = 1

pro_users_config = [
    {"departement_code": "93", "has_adage_eligible_siren": True},
    {"departement_code": "97", "has_adage_eligible_siren": False},
]


def create_industrial_pro_users(offerers_by_name: dict) -> dict[str, User]:
    logger.info("create_industrial_pro_users")

    users_by_name = {}

    offerers = list(offerers_by_name.values())
    adage_eligible_offerers = [offerer for offerer in offerers if offerer.siren == str(MOCK_ADAGE_ELIGIBLE_SIREN)]
    adage_not_eligible_offerers = [offerer for offerer in offerers if offerer.siren != str(MOCK_ADAGE_ELIGIBLE_SIREN)]

    for _, pro_user_config in enumerate(pro_users_config):

        for pro_count in range(PROS_COUNT):
            departement_code = pro_user_config["departement_code"]
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
            user_offerer = (
                adage_eligible_offerers[0]
                if pro_user_config["has_adage_eligible_siren"] == True
                else adage_not_eligible_offerers[0]
            )
            UserOffererFactory(offerer=user_offerer, user=user)

    repository.save(*users_by_name.values())

    logger.info("created %d users", len(users_by_name))

    return users_by_name
