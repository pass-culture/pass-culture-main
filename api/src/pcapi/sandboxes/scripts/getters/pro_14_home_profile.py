from pcapi.core.offers import factories as offers_factories
from pcapi.sandboxes.scripts.utils.helpers import get_pro_helper


def get_pro_user():
    user_offerer = offers_factories.UserOffererFactory(
        validationToken=None,
        offerer__validationToken=None,
        user__validationToken=None,
        user__phoneNumber="01 00 00 00 00",
    )
    venue = offers_factories.VenueFactory(managingOfferer=user_offerer.offerer)
    offers_factories.ThingOfferFactory(venue=venue, isActive=True)

    return {"user": get_pro_helper(user_offerer.user)}
