import logging

from pcapi.core.offerers.factories import UserOffererFactory
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import User
from pcapi.repository import repository
from pcapi.sandboxes.scripts.mocks.educational_siren_mocks import MOCK_ADAGE_ELIGIBLE_SIREN


logger = logging.getLogger(__name__)


def create_industrial_pro_users(offerers_by_name: dict) -> dict[str, User]:
    logger.info("create_industrial_pro_users")

    users_by_name = {}

    offerers = list(offerers_by_name.values())
    adage_eligible_offerers = [offerer for offerer in offerers if offerer.siren == str(MOCK_ADAGE_ELIGIBLE_SIREN)]

    pro_retention = users_factories.ProFactory.create(
        lastName="PRO",
        firstName="Retention",
        email="retention@example.com",
    )
    pro_retention_structures = users_factories.ProFactory.create(
        lastName="PRO",
        firstName="Retention Structures",
        email="retention_structures@example.com",
    )
    pro_adage_eligible = users_factories.ProFactory.create(
        lastName="PC Test Pro",
        firstName="97 0",
        departementCode="97",
        postalCode="97100",
        email="pro_adage_eligible@example.com",
    )
    # Attach all structures to the retention_structures user
    for offerer in offerers:
        UserOffererFactory.create(offerer=offerer, user=pro_retention_structures)
    # Pro retention user for only 1 structure
    UserOffererFactory.create(offerer=offerers[-1], user=pro_retention)
    # Pro user with adage eligible structure
    UserOffererFactory.create(offerer=adage_eligible_offerers[0], user=pro_adage_eligible)

    users_by_name["pro retention"] = pro_retention
    users_by_name["pro retention structures"] = pro_retention_structures
    users_by_name["pro pro adage eligible"] = pro_adage_eligible

    repository.save(*users_by_name.values())

    logger.info("created %d users", len(users_by_name))

    return users_by_name
