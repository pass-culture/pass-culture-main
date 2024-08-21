from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_user_and_venue_helper


def create_pro_user_with_venue() -> dict:
    pro_user = users_factories.ProFactory()
    users_factories.UserProNewNavStateFactory(userId=pro_user.id)
    venue = offerers_factories.VenueFactory()
    offerers_factories.UserOffererFactory(
        user=pro_user,
        offerer=venue.managingOfferer,
    )
    return get_pro_user_and_venue_helper(pro_user, venue)
