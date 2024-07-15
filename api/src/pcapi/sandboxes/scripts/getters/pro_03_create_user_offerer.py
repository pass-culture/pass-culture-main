from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_user_helper


def create_pro_user_new_nav() -> dict:
    pro_user = users_factories.ProFactory()
    users_factories.UserProNewNavStateFactory(user=pro_user)
    return {"user": get_pro_user_helper(pro_user)}


def create_user_with_offerer() -> dict:
    pro_user = users_factories.ProFactory()
    users_factories.UserProNewNavStateFactory(user=pro_user)
    venue = offerers_factories.VenueFactory(
        siret="11006801200050",
        managingOfferer__name="MINISTERE DE LA TRANSITION ECOLOGIQUE ET DE LA COHESION DES TERRITOIRES",
    )
    offerers_factories.UserOffererFactory(
        user=pro_user,
        offerer=venue.managingOfferer,
    )
    return {"user": get_pro_user_helper(pro_user)}
