from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_user_and_venue_helper
from pcapi.sandboxes.scripts.utils.helpers import get_pro_user_helper


# def create_user_new_nav() -> dict:
#     pro_user = users_factories.ProFactory()
#     users_factories.UserProNewNavStateFactory(user=pro_user)
#     return get_pro_user_helper(pro_user)


def create_user_with_venue() -> dict:
    pro_user = users_factories.ProFactory()
    users_factories.UserProNewNavStateFactory(user=pro_user)
    venue = offerers_factories.VenueFactory()
    offerers_factories.UserOffererFactory(
        user=pro_user,
        offerer=venue.managingOfferer,
    )
    return get_pro_user_and_venue_helper(pro_user, venue)
