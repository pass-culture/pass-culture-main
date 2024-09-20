from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_user_helper


def create_pro_user() -> dict:
    pro_user = users_factories.ProFactory()
    return {"user": get_pro_user_helper(pro_user)}
