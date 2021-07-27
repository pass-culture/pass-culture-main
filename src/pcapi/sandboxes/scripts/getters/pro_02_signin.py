from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_existing_pro_validated_user_without_offer() -> dict:
    return {
        "user": get_pro_helper(
            users_factories.ProFactory(
                validationToken=None,
            )
        )
    }
