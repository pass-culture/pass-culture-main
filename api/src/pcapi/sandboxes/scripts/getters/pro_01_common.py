from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_user_helper


def create_user_new_nav() -> dict:
    pro_user = users_factories.ProFactory()
    users_factories.UserProNewNavStateFactory(user=pro_user)
    return {"user": get_pro_user_helper(pro_user)}
