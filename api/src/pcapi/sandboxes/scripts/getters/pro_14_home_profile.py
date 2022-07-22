import pcapi.core.offerers.factories as offerers_factories
import pcapi.core.offers.factories as offers_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_pro_user():  # type: ignore [no-untyped-def]
    user_offerer = offerers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
        user__phoneNumber="+33100000009",
    )
    venue = offerers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    offers_factories.ThingOfferFactory(venue=venue, isActive=True)

    return {"user": get_pro_helper(user_offerer.user)}
